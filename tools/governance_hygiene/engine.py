"""Governance Hygiene Agent orchestration (§9A-5, §GSW write-path order, §GSB reconcile)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from pathlib import Path

from adapters.base import VcsAdapter
from adapters.config import OverseerConfig
from adapters.errors import ReadError, WriteError
from adapters.runner import CommandRunner, quote_arg
from cli.atomic import WriteFailure, atomic_write_text
from tools.governance_hygiene.drift import detect_drift
from tools.governance_hygiene.patch import (
    build_handover_patches,
    build_roadmap_patches,
    extract_paste_ready_block,
)
from tools.governance_hygiene.reads import ReadFailure, perform_verified_reads
from tools.governance_hygiene.realign import execute_realign_guard, plan_realign
from tools.governance_gates import scan_governance_gates
from tools.governance_gates.format import format_pending_gate_lines
from tools.cost_awareness.format import format_cost_awareness_lines
from tools.cost_awareness.surface import build_cost_awareness_report
from tools.verification_evidence_gate import (
    build_verification_evidence_gate,
    format_verification_evidence_gate_line,
)
from tools.independent_second_reviewer import (
    build_independent_second_reviewer_gate,
    format_independent_second_reviewer_gate_line,
)
from tools.governance_hygiene.types import DriftReport, GovernanceSyncResult, PatchPlan, VerifiedReads
from tools.workspace import workspace_relay_footer_state

GOVERNANCE_SYNC_MARKER = "last_governance_sync"


def _emit_governance_gate_footer(
    config: OverseerConfig,
    repo_root: Path,
    *,
    handover_text: str,
    roadmap_text: str,
    emit,
    kit_root: Path | None = None,
) -> tuple[int | None, str]:
    """Append §KH1.9 gate reminders, §PC.7 spend-awareness, and §MR.8 workspace_relay.

    Returns ``(exit_code_or_None, workspace_relay_state)``.
    """
    if config.governance_gates.remind:
        if "governance-sync" in config.governance_gates.surfaces:
            result = scan_governance_gates(
                config,
                repo_root,
                handover_text=handover_text,
                roadmap_text=roadmap_text,
            )
            emit("")
            for line in format_pending_gate_lines(result):
                emit(line)

    if (
        config.cost_awareness.enabled
        and "governance-sync" in config.cost_awareness.surfaces
        and kit_root is not None
    ):
        cost_report = build_cost_awareness_report(
            config,
            repo_root,
            kit_root=kit_root,
            handover_text=handover_text,
            roadmap_text=roadmap_text,
        )
        if cost_report.exit_code == 31:
            emit("")
            emit(cost_report.violation or "routing policy file missing or unreadable")
            relay_state = workspace_relay_footer_state(config, repo_root)
            emit("")
            emit(f"workspace_relay: {relay_state}")
            return 31, relay_state
        emit("")
        for line in format_cost_awareness_lines(cost_report):
            emit(line)

    verification_gate = build_verification_evidence_gate(
        config,
        repo_root,
        handover_text=handover_text,
        roadmap_text=roadmap_text,
    )
    ve_line = format_verification_evidence_gate_line(verification_gate)
    if ve_line:
        emit("")
        emit(ve_line)
        if (
            not verification_gate.ok
            and verification_gate.mode == "require"
            and verification_gate.token == "missing_verification_evidence"
        ):
            relay_state = workspace_relay_footer_state(config, repo_root)
            emit("")
            emit(f"workspace_relay: {relay_state}")
            return 2, relay_state

    isr_gate = build_independent_second_reviewer_gate(
        config,
        repo_root,
        handover_text=handover_text,
        roadmap_text=roadmap_text,
    )
    isr_line = format_independent_second_reviewer_gate_line(isr_gate)
    if isr_line:
        emit("")
        emit(isr_line)
        if isr_gate.remediation:
            emit(isr_gate.remediation)
        if (
            not isr_gate.ok
            and isr_gate.mode == "require"
            and isr_gate.token == "missing_independent_second_review"
        ):
            relay_state = workspace_relay_footer_state(config, repo_root)
            emit("")
            emit(f"workspace_relay: {relay_state}")
            return 2, relay_state

    relay_state = workspace_relay_footer_state(config, repo_root)
    emit("")
    emit(f"workspace_relay: {relay_state}")
    if relay_state not in {"not_configured", "ok"}:
        emit(
            "multi-repo SD-17 incomplete until ok workspace check-next exits 0 "
            "(refresh relay tips; no peer writes from this command)"
        )
    return None, relay_state


def run_governance_sync(
    config: OverseerConfig,
    repo_root: Path,
    adapter: VcsAdapter,
    runner: CommandRunner,
    *,
    dry_run: bool = True,
    lane: str | None = None,
    all_lanes: bool = False,
    emit,
    kit_root: Path | None = None,
) -> GovernanceSyncResult:
    """Execute governance-sync; default dry-run is inert (§7)."""
    if all_lanes and lane is not None:
        return GovernanceSyncResult(
            exit_code=2,
            dry_run=dry_run,
            reads=None,
            drift=None,
            plan=None,
            committed=False,
            commit_sha=None,
            messages=("cannot use --lane with --all-lanes",),
        )

    if all_lanes:
        return _run_all_lanes(
            config,
            repo_root,
            adapter,
            runner,
            dry_run=dry_run,
            emit=emit,
            kit_root=kit_root,
        )

    lane_name = lane
    if config.docs.lanes is not None and lane is None:
        lane_name = config.docs.default_lane
    return _run_single_lane(
        config,
        repo_root,
        adapter,
        runner,
        lane=lane_name,
        dry_run=dry_run,
        skip_missing=False,
        emit=emit,
        kit_root=kit_root,
    )


def _run_all_lanes(
    config: OverseerConfig,
    repo_root: Path,
    adapter: VcsAdapter,
    runner: CommandRunner,
    *,
    dry_run: bool,
    emit,
    kit_root: Path | None = None,
) -> GovernanceSyncResult:
    """Sync every configured lane; skip lanes with missing doc files (§K8)."""
    if config.docs.lanes is None:
        lane_names: tuple[str | None, ...] = (None,)
    else:
        lane_names = tuple(sorted(config.docs.lanes.keys()))

    last_result: GovernanceSyncResult | None = None
    for lane_name in lane_names:
        name_label = lane_name if lane_name is not None else "default"
        emit(f"lane: {name_label}")
        result = _run_single_lane(
            config,
            repo_root,
            adapter,
            runner,
            lane=lane_name,
            dry_run=dry_run,
            skip_missing=True,
            emit=emit,
            kit_root=kit_root,
        )
        last_result = result
        if result.exit_code == 4:
            emit(f"skipping lane {name_label}: missing governance doc(s)")
            continue
        if result.exit_code != 0:
            return result
    if last_result is None:
        return GovernanceSyncResult(
            exit_code=0,
            dry_run=dry_run,
            reads=None,
            drift=None,
            plan=None,
            committed=False,
            commit_sha=None,
            messages=("no lanes configured",),
        )
    return last_result


def _run_single_lane(
    config: OverseerConfig,
    repo_root: Path,
    adapter: VcsAdapter,
    runner: CommandRunner,
    *,
    lane: str | None,
    dry_run: bool,
    skip_missing: bool,
    emit,
    kit_root: Path | None = None,
) -> GovernanceSyncResult:
    """Sync one handover + roadmap pair."""
    from adapters.config import resolve_lane_docs
    from cli.docs_paths import lane_living_doc_abs

    try:
        lane_docs = resolve_lane_docs(config, lane)
    except Exception as exc:
        from adapters.errors import ConfigError

        if isinstance(exc, ConfigError):
            return GovernanceSyncResult(
                exit_code=2,
                dry_run=dry_run,
                reads=None,
                drift=None,
                plan=None,
                committed=False,
                commit_sha=None,
                messages=(str(exc),),
            )
        raise

    handover_path = lane_living_doc_abs(repo_root, config, lane_docs, lane_docs.handover)
    roadmap_path = lane_living_doc_abs(repo_root, config, lane_docs, lane_docs.roadmap)

    for path in (handover_path, roadmap_path):
        if not path.is_file():
            if skip_missing:
                return GovernanceSyncResult(
                    exit_code=4,
                    dry_run=dry_run,
                    reads=None,
                    drift=None,
                    plan=None,
                    committed=False,
                    commit_sha=None,
                    messages=(f"missing governance doc: {path.name}",),
                )
            return GovernanceSyncResult(
                exit_code=4,
                dry_run=dry_run,
                reads=None,
                drift=None,
                plan=None,
                committed=False,
                commit_sha=None,
                messages=(f"missing governance doc: {path.name}",),
            )

    reads = perform_verified_reads(config, adapter, runner, repo_root=repo_root)
    if isinstance(reads, ReadFailure):
        emit(f"read failed [{reads.regime}]: {reads.command}")
        emit(reads.message)
        return GovernanceSyncResult(
            exit_code=2,
            dry_run=dry_run,
            reads=None,
            drift=None,
            plan=None,
            committed=False,
            commit_sha=None,
            messages=(reads.message,),
            error_command=reads.command,
        )

    handover_text = handover_path.read_text(encoding="utf-8")
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    drift = detect_drift(reads, handover_text, roadmap_text)

    if drift.any_unreadable:
        emit("drift detection unreadable — fail-closed")
        return GovernanceSyncResult(
            exit_code=2,
            dry_run=dry_run,
            reads=reads,
            drift=drift,
            plan=None,
            committed=False,
            commit_sha=None,
            messages=("unreadable drift field",),
        )

    if drift.fully_aligned:
        emit("governance-sync: aligned (D1–D3)")
        _write_sync_marker(repo_root, reads)
        footer_code, workspace_relay = _emit_governance_gate_footer(
            config,
            repo_root,
            handover_text=handover_text,
            roadmap_text=roadmap_text,
            emit=emit,
            kit_root=kit_root,
        )
        return GovernanceSyncResult(
            exit_code=footer_code or 0,
            dry_run=dry_run,
            reads=reads,
            drift=drift,
            plan=None,
            committed=False,
            commit_sha=None,
            messages=("aligned",),
            workspace_relay=workspace_relay,
        )

    realign_planned, _ = plan_realign(config, adapter, reads, drift)
    realign_summary, realign_error = execute_realign_guard(
        config,
        adapter,
        reads,
        drift,
        dry_run=True,
    )
    if realign_error:
        emit(f"realign dry-run failed: {realign_error}")
        return GovernanceSyncResult(
            exit_code=2,
            dry_run=dry_run,
            reads=reads,
            drift=drift,
            plan=None,
            committed=False,
            commit_sha=None,
            messages=(realign_error,),
            error_command=realign_error,
        )

    # §GSP.6.1: roadmap patches first so handover NEXT regen sees D3-reconciled queue.
    patched_roadmap, roadmap_sections = build_roadmap_patches(
        roadmap_text,
        reads,
        drift,
    )
    patched_handover, handover_sections, next_regen_token = build_handover_patches(
        handover_text,
        reads,
        drift,
        realign_summary=realign_summary,
        config=config,
        roadmap_text=patched_roadmap,
        repo_root=repo_root,
    )
    sections = handover_sections + roadmap_sections

    feature_branch = _feature_branch_name(config)
    main_sha = reads.r1_github_main_sha or reads.r3_canonical_main_sha or reads.r2_anchor_sha
    commit_message = _commit_message(main_sha, drift, sections, realign_summary)
    pr_url = _build_pr_url(runner, repo_root, config, feature_branch)

    plan = PatchPlan(
        handover_text=patched_handover,
        roadmap_text=patched_roadmap,
        patched_sections=sections,
        realign_planned=realign_planned,
        realign_reason=realign_summary,
        feature_branch=feature_branch,
        commit_message=commit_message,
        pr_url=pr_url,
    )

    emit(f"drift: D1={drift.d1_handover_vs_git} D2={drift.d2_anchor_vs_canonical} D3={drift.d3_queue_vs_merged}")
    emit(f"planned sections: {', '.join(sections)}")
    emit(next_regen_token)
    if realign_summary:
        emit(realign_summary)
    if dry_run and "land-b" in next_regen_token:
        # §PMHF.3.4 rule 4: dry-run shows the planned land-b body.
        land_b_block = extract_paste_ready_block(patched_handover)
        if land_b_block:
            emit(land_b_block)
    if dry_run:
        d1_d2_aligned = (
            drift.d1_handover_vs_git == "aligned"
            and drift.d2_anchor_vs_canonical == "aligned"
        )
        if d1_d2_aligned:
            _write_sync_marker(repo_root, reads)
            emit(
                "dry-run: no governance-doc writes, commits, or realign apply "
                "(may stamp local .overseer/last_governance_sync when D1/D2 aligned)"
            )
        else:
            emit("dry-run: no writes, commits, or realign apply")
        if pr_url:
            emit(f"docs-only PR URL (operator-gated): {pr_url}")
        footer_code, workspace_relay = _emit_governance_gate_footer(
            config,
            repo_root,
            handover_text=handover_text,
            roadmap_text=roadmap_text,
            emit=emit,
            kit_root=kit_root,
        )
        return GovernanceSyncResult(
            exit_code=footer_code or 0,
            dry_run=True,
            reads=reads,
            drift=drift,
            plan=plan,
            committed=False,
            commit_sha=None,
            messages=("dry-run plan",),
            workspace_relay=workspace_relay,
        )

    return _apply_plan(
        config=config,
        repo_root=repo_root,
        adapter=adapter,
        runner=runner,
        reads=reads,
        drift=drift,
        plan=plan,
        handover_path=handover_path,
        roadmap_path=roadmap_path,
        emit=emit,
        kit_root=kit_root,
        handover_text=handover_text,
        roadmap_text=roadmap_text,
    )


def _apply_plan(
    *,
    config: OverseerConfig,
    repo_root: Path,
    adapter: VcsAdapter,
    runner: CommandRunner,
    reads: VerifiedReads,
    drift: DriftReport,
    plan: PatchPlan,
    handover_path: Path,
    roadmap_path: Path,
    emit,
    kit_root: Path | None = None,
    handover_text: str = "",
    roadmap_text: str = "",
) -> GovernanceSyncResult:
    """Apply patches, commit, and push on a feature branch.

    Frozen §GSW.3.1 order: capture original branch state → realign on the
    original branch → ensure feature branch (dual-HEAD under
    ``muse+git-mirror``, §GSW.5.1) → write doc patches → commit → sync
    marker (only after successful commit, §GSW.3.4) → push. Any failure
    after the feature-branch switch restores docs + marker + original
    branch (§GSW.4.2).

    §GSB amends step C only: a C0 reconcile of the dated sync-branch name
    (fast-forward ancestor tips / deterministic ``-N`` uniquify) runs before
    the C1 dual-HEAD ensure, so a same-day second ``--write`` never checks
    out a stale tip into the shared working tree (§GSB.3.1–§GSB.3.4).
    """
    original_handover = handover_path.read_text(encoding="utf-8")
    original_roadmap = roadmap_path.read_text(encoding="utf-8")
    marker_path = repo_root / ".overseer" / GOVERNANCE_SYNC_MARKER
    prior_marker = (
        marker_path.read_text(encoding="utf-8") if marker_path.is_file() else None
    )

    def _failure(exit_code: int, message: str, error_command: str | None) -> GovernanceSyncResult:
        return GovernanceSyncResult(
            exit_code=exit_code,
            dry_run=False,
            reads=reads,
            drift=drift,
            plan=plan,
            committed=False,
            commit_sha=None,
            messages=(message,),
            error_command=error_command,
        )

    # Step A (§GSW.4.1): capture branch identity before any mutation.
    branch_state, capture_command = _capture_branch_state(config, adapter, runner, repo_root)
    if branch_state is None:
        emit(f"branch capture failed: {capture_command}")
        return _failure(2, f"branch capture failed: {capture_command}", capture_command)

    # Step B (§GSW.3.1): realign guard on the original branch — before any
    # feature-branch switch and before any doc write.
    realign_summary, realign_error = execute_realign_guard(
        config,
        adapter,
        reads,
        drift,
        dry_run=False,
    )
    if realign_error:
        emit(f"realign failed: {realign_error}")
        return _failure(2, realign_error, realign_error)

    def _rollback(*, restore_docs: bool) -> None:
        _rollback_apply(
            config=config,
            repo_root=repo_root,
            adapter=adapter,
            runner=runner,
            handover_path=handover_path,
            roadmap_path=roadmap_path,
            original_handover=original_handover,
            original_roadmap=original_roadmap,
            marker_path=marker_path,
            prior_marker=prior_marker,
            branch_state=branch_state,
            restore_docs=restore_docs,
            emit=emit,
        )

    # Step C0 (§GSB.3.2–§GSB.3.3): reconcile the dated sync-branch name on
    # every applicable history before any checkout of that name. Ancestor or
    # equal tips → fast-forward without checkout-as-FF; any diverged history
    # → deterministic -N uniquify of the shared name.
    reconciled, reconcile_error = _reconcile_feature_branch(
        adapter, runner, repo_root, config, plan.feature_branch, branch_state
    )
    if reconcile_error is not None:
        _rollback(restore_docs=False)
        emit(reconcile_error)
        return _failure(2, reconcile_error, reconcile_error)
    if reconciled != plan.feature_branch:
        # §GSB.3.3: PatchPlan is frozen — replace it so the success-path
        # commit, push, and result plan all observe the reconciled branch
        # and a pr_url rebuilt for that branch.
        plan = replace(
            plan,
            feature_branch=reconciled,
            pr_url=_build_pr_url(runner, repo_root, config, reconciled),
        )
        emit(f"governance-sync branch uniquified: {reconciled}")

    # Step C1 (§GSW.5): feature branch must exist and hold current HEAD(s)
    # before any handover/roadmap patch write.
    checkout = _ensure_feature_branch(
        adapter, runner, repo_root, config, plan.feature_branch, branch_state
    )
    if checkout is not None:
        _rollback(restore_docs=False)
        emit(checkout)
        return _failure(2, checkout, checkout)

    # Step D: write doc patch bytes (tree now dirty on the feature branch).
    try:
        atomic_write_text(handover_path, plan.handover_text)
        atomic_write_text(roadmap_path, plan.roadmap_text)
    except WriteFailure as exc:
        _rollback(restore_docs=True)
        emit(f"write failed: {exc}")
        return _failure(5, str(exc), None)

    # Step E: commit dirty docs already on the feature branch (§GSW.6).
    rel_handover = _repo_relative(repo_root, handover_path)
    rel_roadmap = _repo_relative(repo_root, roadmap_path)
    commit = adapter.commit_feature(
        branch=plan.feature_branch,
        message=plan.commit_message,
        paths=[rel_handover, rel_roadmap],
    )
    if isinstance(commit, (ReadError, WriteError)):
        _rollback(restore_docs=True)
        cmd = commit.command if hasattr(commit, "command") else "commit_feature"
        emit(str(commit))
        return _failure(2, str(commit), cmd)

    # Step F (§GSW.3.4): stamp the sync marker only after commit success.
    if (
        drift.d1_handover_vs_git == "aligned"
        and drift.d2_anchor_vs_canonical == "aligned"
    ):
        _write_sync_marker(repo_root, reads)

    # Step G: feature-branch push (Tier 1, regime-appropriate).
    push_error = _push_feature_branch(runner, repo_root, config, plan.feature_branch)
    if push_error:
        emit(push_error)

    if plan.pr_url:
        emit(f"docs-only PR URL (operator-gated — do not auto-open): {plan.pr_url}")

    _, workspace_relay = _emit_governance_gate_footer(
        config,
        repo_root,
        handover_text=handover_text or plan.handover_text,
        roadmap_text=roadmap_text or plan.roadmap_text,
        emit=emit,
        kit_root=kit_root,
    )
    return GovernanceSyncResult(
        exit_code=0,
        dry_run=False,
        reads=reads,
        drift=drift,
        plan=plan,
        committed=commit.committed,
        commit_sha=commit.sha,
        messages=("applied",),
        workspace_relay=workspace_relay,
    )


def _feature_branch_name(config: OverseerConfig) -> str:
    slug = f"governance-sync-{date.today().isoformat()}"
    pattern = config.vcs.git.feature_branch_pattern
    return pattern.replace("{slug}", slug)


def _commit_message(
    main_sha: str,
    drift: DriftReport,
    sections: tuple[str, ...],
    realign_summary: str | None,
) -> str:
    drift_tokens = (
        f"D1={drift.d1_handover_vs_git},"
        f"D2={drift.d2_anchor_vs_canonical},"
        f"D3={drift.d3_queue_vs_merged}"
    )
    subject = f"chore(governance): sync handover+roadmap to {main_sha[:7]} (drift: {drift_tokens})"
    body_lines = ["Patched sections:", *[f"- {name}" for name in sections]]
    if realign_summary:
        body_lines.append(f"Realign: {realign_summary}")
    return subject + "\n\n" + "\n".join(body_lines)


def _build_pr_url(
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    feature_branch: str,
) -> str | None:
    if config.vcs.regime == "muse-only":
        return None
    remote = config.vcs.git.remote
    main = config.vcs.git.main_branch
    cmd = f"git remote get-url {quote_arg(remote)}"
    result = runner.run(cmd, cwd=str(repo_root))
    if not result.ok:
        return f"https://github.com/<owner>/<repo>/compare/{main}...{feature_branch}?expand=1"
    owner_repo = _parse_github_remote(result.stdout.strip())
    if not owner_repo:
        return f"https://github.com/<owner>/<repo>/compare/{main}...{feature_branch}?expand=1"
    owner, repo = owner_repo
    return f"https://github.com/{owner}/{repo}/compare/{main}...{feature_branch}?expand=1"


def _parse_github_remote(url: str) -> tuple[str, str] | None:
    ssh = re.match(r"git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
    if ssh:
        return ssh.group("owner"), ssh.group("repo")
    https = re.match(r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
    if https:
        return https.group("owner"), https.group("repo")
    return None


def _write_sync_marker(repo_root: Path, reads: VerifiedReads | None = None) -> None:
    """Write enriched ``last_governance_sync`` marker (§GFG.5.2)."""
    marker = repo_root / ".overseer" / GOVERNANCE_SYNC_MARKER
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    r1 = ""
    r3 = ""
    if reads is not None:
        r1 = reads.r1_github_main_sha or ""
        r3 = reads.r3_canonical_main_sha or ""
    body = f"{stamp}\nr1={r1}\nr3={r3}\n"
    atomic_write_text(marker, body)


def _repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


@dataclass(frozen=True)
class BranchState:
    """Regime-specific ``original_branch_state`` captured at step A (§GSW.4.1)."""

    git_branch: str | None
    muse_branch: str | None


def _muse_command_prefix(adapter: VcsAdapter, repo_root: Path) -> str:
    muse_cwd = str(getattr(adapter, "muse_cwd", repo_root))
    return f"muse -C {quote_arg(muse_cwd)}"


def _capture_branch_state(
    config: OverseerConfig,
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
) -> tuple[BranchState | None, str | None]:
    """Capture current branch identity per regime; fail closed on unreadable HEAD.

    Returns ``(state, None)`` on success or ``(None, failing_command)``.
    """
    root = str(repo_root)
    regime = config.vcs.regime
    git_branch: str | None = None
    muse_branch: str | None = None

    if regime in {"git-only", "muse+git-mirror"}:
        command = "git rev-parse --abbrev-ref HEAD"
        result = runner.run(command, cwd=root)
        if not result.ok or not result.stdout.strip():
            return None, command
        git_branch = result.stdout.strip()

    if regime in {"muse-only", "muse+git-mirror"}:
        command = f"{_muse_command_prefix(adapter, repo_root)} rev-parse --abbrev-ref HEAD"
        result = runner.run(command, cwd=root)
        if not result.ok or not result.stdout.strip():
            return None, command
        muse_branch = result.stdout.strip()

    return BranchState(git_branch=git_branch, muse_branch=muse_branch), None


def _ensure_feature_branch(
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    branch: str,
    state: BranchState,
) -> str | None:
    """Place current HEAD(s) on ``branch`` before any doc write (§GSW.5).

    Under ``muse+git-mirror`` both the Muse HEAD and the Git HEAD must be on
    ``branch`` (§GSW.5.1 dual-HEAD rule). Returns the failing command, or
    ``None`` on success.
    """
    regime = config.vcs.regime
    if regime in {"muse-only", "muse+git-mirror"}:
        muse_error = _ensure_muse_branch(adapter, runner, repo_root, branch, state.muse_branch)
        if muse_error is not None:
            return muse_error
    if regime in {"git-only", "muse+git-mirror"}:
        git_error = _ensure_git_branch(runner, repo_root, branch, state.git_branch)
        if git_error is not None:
            return git_error
    return None


def _ensure_muse_branch(
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    branch: str,
    current: str | None,
) -> str | None:
    """Create/switch the Muse HEAD to ``branch`` (§GSW.5.2).

    Switch to an existing branch retries with ``--autoshelf`` so uncommitted
    tracked changes carry across the checkout (§GSW.6.2 allowed secondary
    guard; bare-checkout-only is the live defect, ``--force`` is forbidden).
    """
    if current == branch:
        return None
    root = str(repo_root)
    prefix = _muse_command_prefix(adapter, repo_root)
    create = runner.run(f"{prefix} checkout -b {quote_arg(branch)}", cwd=root)
    if create.ok:
        return None
    switch_cmd = f"{prefix} checkout {quote_arg(branch)}"
    if runner.run(switch_cmd, cwd=root).ok:
        return None
    carry_cmd = f"{prefix} checkout --autoshelf {quote_arg(branch)}"
    if runner.run(carry_cmd, cwd=root).ok:
        return None
    return carry_cmd


def _ensure_git_branch(
    runner: CommandRunner,
    repo_root: Path,
    branch: str,
    current: str | None,
) -> str | None:
    """Create/switch the Git HEAD to ``branch`` (git carries dirty changes)."""
    if current == branch:
        return None
    root = str(repo_root)
    create = runner.run(f"git checkout -b {quote_arg(branch)}", cwd=root)
    if create.ok:
        return None
    switch_cmd = f"git checkout {quote_arg(branch)}"
    if runner.run(switch_cmd, cwd=root).ok:
        return None
    return switch_cmd


_UNIQUIFY_LIMIT = 100


@dataclass(frozen=True)
class _BranchReconcileProbe:
    """Per-history §GSB.3.2 classification of the candidate dated branch.

    ``tip`` is ``T_exist`` and ``target`` is ``T_target`` in that history's
    own id space (Git SHAs vs Muse ``sha256:`` ids are never cross-compared).
    """

    exists: bool
    tip: str | None = None
    target: str | None = None
    ancestor: bool = False


def _reconcile_feature_branch(
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    branch: str,
    state: BranchState,
) -> tuple[str, str | None]:
    """C0 reconcile of the dated sync-branch name before ensure (§GSB.3).

    Classifies the existing branch tip against ``T_target`` on every
    applicable history. All existing sides ancestor/equal → fast-forward
    the tips without checking ``branch`` out; any diverged side →
    deterministic ``-N`` uniquify of the shared name (§GSB.3.2 cross-history
    rule). Returns ``(reconciled_branch, failing_command_or_None)``.
    """
    regime = config.vcs.regime
    muse_probe: _BranchReconcileProbe | None = None
    git_probe: _BranchReconcileProbe | None = None

    if regime in {"muse-only", "muse+git-mirror"}:
        muse_probe, error = _classify_muse_branch(
            adapter, runner, repo_root, config, branch, state.muse_branch
        )
        if error is not None:
            return branch, error
    if regime in {"git-only", "muse+git-mirror"}:
        git_probe, error = _classify_git_branch(
            runner, repo_root, config, branch, state.git_branch
        )
        if error is not None:
            return branch, error

    existing = [p for p in (muse_probe, git_probe) if p is not None and p.exists]
    if not existing:
        return branch, None

    # §GSB.3.2 cross-history rule: if either side diverged, uniquify the
    # shared name — never FF one history and uniquify the other under the
    # same name.
    if any(not probe.ancestor for probe in existing):
        return _uniquify_branch(adapter, runner, repo_root, config, branch)

    if muse_probe is not None and muse_probe.exists and muse_probe.tip != muse_probe.target:
        error = _fast_forward_muse(
            adapter, runner, repo_root, branch, muse_probe.target or "", state.muse_branch
        )
        if error is not None:
            return branch, error
    if git_probe is not None and git_probe.exists and git_probe.tip != git_probe.target:
        error = _fast_forward_git(
            runner, repo_root, branch, git_probe.target or "", state.git_branch
        )
        if error is not None:
            return branch, error
    return branch, None


def _classify_git_branch(
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    branch: str,
    original: str | None,
) -> tuple[_BranchReconcileProbe | None, str | None]:
    """Probe existence + §GSB.3.2 ancestor classification on the Git history."""
    root = str(repo_root)
    probe_cmd = f"git rev-parse --verify {quote_arg('refs/heads/' + branch)}"
    probe = runner.run(probe_cmd, cwd=root)
    if not probe.ok:
        return _BranchReconcileProbe(exists=False), None
    t_exist = probe.stdout.strip()
    if not t_exist:
        return None, probe_cmd

    # §GSB.3.2.1 reconcile base ref: O_H when HEAD is elsewhere; configured
    # main when HEAD already names the dated branch.
    base_ref = original if original and original != branch else config.vcs.git.main_branch
    target_cmd = f"git rev-parse {quote_arg(base_ref)}"
    target = runner.run(target_cmd, cwd=root)
    if not target.ok or not target.stdout.strip():
        return None, target_cmd
    t_target = target.stdout.strip()

    if t_exist == t_target:
        return _BranchReconcileProbe(True, t_exist, t_target, True), None
    ancestor_cmd = (
        f"git merge-base --is-ancestor {quote_arg(t_exist)} {quote_arg(t_target)}"
    )
    result = runner.run(ancestor_cmd, cwd=root)
    if result.exit_code == 0:
        return _BranchReconcileProbe(True, t_exist, t_target, True), None
    if result.exit_code == 1:
        return _BranchReconcileProbe(True, t_exist, t_target, False), None
    return None, ancestor_cmd


def _classify_muse_branch(
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    branch: str,
    original: str | None,
) -> tuple[_BranchReconcileProbe | None, str | None]:
    """Probe existence + §GSB.3.2 ancestor classification on the Muse history."""
    root = str(repo_root)
    prefix = _muse_command_prefix(adapter, repo_root)
    probe_cmd = f"{prefix} rev-parse {quote_arg(branch)}"
    probe = runner.run(probe_cmd, cwd=root)
    if not probe.ok:
        return _BranchReconcileProbe(exists=False), None
    t_exist = probe.stdout.strip()
    if not t_exist:
        return None, probe_cmd

    base_ref = (
        original
        if original and original != branch
        else (config.vcs.muse.main_branch or "")
    )
    target_cmd = f"{prefix} rev-parse {quote_arg(base_ref)}"
    if not base_ref:
        return None, target_cmd
    target = runner.run(target_cmd, cwd=root)
    if not target.ok or not target.stdout.strip():
        return None, target_cmd
    t_target = target.stdout.strip()

    if t_exist == t_target:
        return _BranchReconcileProbe(True, t_exist, t_target, True), None
    # Muse 0.2.x has no --is-ancestor flag; the LCA equals T_exist exactly
    # when T_exist is an ancestor of T_target.
    ancestor_cmd = (
        f"{prefix} merge-base --json {quote_arg(t_exist)} {quote_arg(t_target)}"
    )
    result = runner.run(ancestor_cmd, cwd=root)
    if not result.ok:
        return None, ancestor_cmd
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, ancestor_cmd
    if not isinstance(payload, dict):
        return None, ancestor_cmd
    ancestor = payload.get("merge_base") == t_exist
    return _BranchReconcileProbe(True, t_exist, t_target, ancestor), None


def _fast_forward_git(
    runner: CommandRunner,
    repo_root: Path,
    branch: str,
    target: str,
    original: str | None,
) -> str | None:
    """§GSB.3.3 Git fast-forward: ancestor-validated tip move, never checkout-as-FF.

    Returns the failing command (or a clobber-refusal message) or ``None``.
    """
    root = str(repo_root)
    if original != branch:
        ff_cmd = f"git branch -f {quote_arg(branch)} {quote_arg(target)}"
        if not runner.run(ff_cmd, cwd=root).ok:
            return ff_cmd
        return None

    # O_H == B (§GSB.3.2.1): git branch -f refuses the checked-out branch,
    # so move the ref directly, then refresh the stale worktree without
    # checkout --force (§GSB.3.3 / §GSB.3.4).
    status_cmd = "git status --porcelain"
    pre = runner.run(status_cmd, cwd=root)
    if not pre.ok:
        return status_cmd
    pre_dirty = bool(pre.stdout.strip())
    update_cmd = f"git update-ref {quote_arg('refs/heads/' + branch)} {quote_arg(target)}"
    if not runner.run(update_cmd, cwd=root).ok:
        return update_cmd
    post = runner.run(status_cmd, cwd=root)
    if not post.ok:
        return status_cmd
    if not post.stdout.strip():
        return None
    if pre_dirty:
        # Uncommitted operator work is mixed into the stale tree — a refresh
        # would clobber it. Fail closed (§GSB.3.3).
        return f"worktree refresh after {update_cmd} would clobber uncommitted changes"
    # Tree was clean at T_exist, so the only difference is committed stale
    # content — a clean-tree-verified reset discards nothing uncommitted.
    reset_cmd = f"git reset --hard {quote_arg(target)}"
    if not runner.run(reset_cmd, cwd=root).ok:
        return reset_cmd
    return None


def _fast_forward_muse(
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    branch: str,
    target: str,
    original: str | None,
) -> str | None:
    """§GSB.3.3 Muse fast-forward via ``muse update-ref`` (never checkout).

    When Muse HEAD already names the dated branch, a tip-only move leaves
    the shared worktree stale; refresh uses a clean-tree-verified
    ``muse reset --hard`` (live Muse refuses it on tracked changes, so it
    can never clobber operator work) — ``--force`` stays forbidden.
    """
    root = str(repo_root)
    prefix = _muse_command_prefix(adapter, repo_root)
    update_cmd = f"{prefix} update-ref {quote_arg(branch)} {quote_arg(target)}"
    if original != branch:
        if not runner.run(update_cmd, cwd=root).ok:
            return update_cmd
        return None

    pre_dirty, error = _muse_tracked_dirty(runner, repo_root, prefix)
    if error is not None:
        return error
    if not pre_dirty:
        # Worktree matches T_exist bytes exactly: reset --hard while still
        # clean refreshes worktree + tip together (discarding only committed
        # T_exist content); update-ref then locks the frozen tip form.
        reset_cmd = f"{prefix} reset {quote_arg(target)} --hard"
        if not runner.run(reset_cmd, cwd=root).ok:
            return reset_cmd
        if not runner.run(update_cmd, cwd=root).ok:
            return update_cmd
        return None

    # Tracked changes present relative to the stale tip: this is either the
    # live mirror shape (shared worktree already holds T_target bytes) or
    # uncommitted operator work. Move the tip, then verify the worktree
    # matches the new tip; anything else fails closed (§GSB.3.4).
    if not runner.run(update_cmd, cwd=root).ok:
        return update_cmd
    post_dirty, error = _muse_tracked_dirty(runner, repo_root, prefix)
    if error is not None:
        return error
    if post_dirty:
        return f"worktree refresh after {update_cmd} would clobber uncommitted changes"
    return None


def _muse_tracked_dirty(
    runner: CommandRunner,
    repo_root: Path,
    prefix: str,
) -> tuple[bool | None, str | None]:
    """Tracked-change dirtiness via ``muse status --json`` (§GSB.3.4).

    Muse 0.2.x sets ``dirty`` for untracked files too; staleness/clobber
    checks must key on tracked changes (``total_changes``) only.
    """
    status_cmd = f"{prefix} status --json"
    result = runner.run(status_cmd, cwd=str(repo_root))
    if not result.ok:
        return None, status_cmd
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, status_cmd
    if not isinstance(payload, dict):
        return None, status_cmd
    total = payload.get("total_changes")
    if isinstance(total, int):
        return total > 0, None
    if "dirty" in payload:
        return bool(payload["dirty"]), None
    return None, status_cmd


def _uniquify_branch(
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    branch: str,
) -> tuple[str, str | None]:
    """§GSB.3.3 deterministic uniquify: lowest ``-N`` (N≥2) free everywhere.

    The diverged existing branch is never deleted, rewound, or force-checked
    out; the suffix contains no secrets, paths, or hostnames.
    """
    regime = config.vcs.regime
    root = str(repo_root)
    prefix = (
        _muse_command_prefix(adapter, repo_root) if regime != "git-only" else None
    )
    for suffix in range(2, _UNIQUIFY_LIMIT):
        candidate = f"{branch}-{suffix}"
        taken = False
        if prefix is not None:
            taken = runner.run(
                f"{prefix} rev-parse {quote_arg(candidate)}", cwd=root
            ).ok
        if not taken and regime in {"git-only", "muse+git-mirror"}:
            taken = runner.run(
                f"git rev-parse --verify {quote_arg('refs/heads/' + candidate)}",
                cwd=root,
            ).ok
        if not taken:
            return candidate, None
    return branch, f"could not uniquify branch {branch!r} within -{_UNIQUIFY_LIMIT - 1}"


def _rollback_apply(
    *,
    config: OverseerConfig,
    repo_root: Path,
    adapter: VcsAdapter,
    runner: CommandRunner,
    handover_path: Path,
    roadmap_path: Path,
    original_handover: str,
    original_roadmap: str,
    marker_path: Path,
    prior_marker: str | None,
    branch_state: BranchState,
    restore_docs: bool,
    emit,
) -> None:
    """Restore docs → marker → original branch on mid-apply failure (§GSW.4.2).

    Doc bytes are restored first so the tree is clean before the restore
    checkout (§GSW.4.3); branch restore is best-effort on both histories and
    never uses ``--force``.
    """
    if restore_docs:
        atomic_write_text(handover_path, original_handover)
        atomic_write_text(roadmap_path, original_roadmap)

    _restore_marker(marker_path, prior_marker)

    for failed_command in _restore_branch_state(
        config, adapter, runner, repo_root, branch_state
    ):
        emit(f"branch restore failed: {failed_command}")


def _restore_marker(marker_path: Path, prior_marker: str | None) -> None:
    """Leave no new stamp behind on mid-apply failure (§GSW.3.4)."""
    if prior_marker is None:
        if marker_path.is_file():
            marker_path.unlink()
        return
    if not marker_path.is_file() or marker_path.read_text(encoding="utf-8") != prior_marker:
        atomic_write_text(marker_path, prior_marker)


def _restore_branch_state(
    config: OverseerConfig,
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    state: BranchState,
) -> tuple[str, ...]:
    """Best-effort restore of captured branch identity on both histories.

    Returns the failing commands (empty on success). If one side fails the
    other is still attempted (§GSW.4.2 dual restore).
    """
    root = str(repo_root)
    regime = config.vcs.regime
    errors: list[str] = []

    if regime in {"muse-only", "muse+git-mirror"} and state.muse_branch:
        prefix = _muse_command_prefix(adapter, repo_root)
        probe = runner.run(f"{prefix} rev-parse --abbrev-ref HEAD", cwd=root)
        current = probe.stdout.strip() if probe.ok else None
        if current != state.muse_branch:
            restore_cmd = f"{prefix} checkout {quote_arg(state.muse_branch)}"
            if not runner.run(restore_cmd, cwd=root).ok:
                carry_cmd = f"{prefix} checkout --autoshelf {quote_arg(state.muse_branch)}"
                if not runner.run(carry_cmd, cwd=root).ok:
                    errors.append(carry_cmd)

    if regime in {"git-only", "muse+git-mirror"} and state.git_branch:
        probe = runner.run("git rev-parse --abbrev-ref HEAD", cwd=root)
        current = probe.stdout.strip() if probe.ok else None
        if current != state.git_branch:
            restore_cmd = f"git checkout {quote_arg(state.git_branch)}"
            if not runner.run(restore_cmd, cwd=root).ok:
                errors.append(restore_cmd)

    return tuple(errors)


def _push_feature_branch(
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    branch: str,
) -> str | None:
    if config.vcs.regime == "muse-only":
        return None
    remote = config.vcs.git.remote
    cmd = f"git push -u {quote_arg(remote)} {quote_arg(branch)}"
    result = runner.run(cmd, cwd=str(repo_root))
    if not result.ok:
        return cmd
    return None

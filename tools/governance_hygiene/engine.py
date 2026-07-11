"""Governance Hygiene Agent orchestration (§9A-5)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from adapters.base import VcsAdapter
from adapters.config import OverseerConfig
from adapters.errors import ReadError, WriteError
from adapters.runner import CommandRunner, quote_arg
from cli.atomic import WriteFailure, atomic_write_text
from tools.governance_hygiene.drift import detect_drift
from tools.governance_hygiene.patch import build_handover_patches, build_roadmap_patches
from tools.governance_hygiene.reads import ReadFailure, perform_verified_reads
from tools.governance_hygiene.realign import execute_realign_guard, plan_realign
from tools.governance_hygiene.types import DriftReport, GovernanceSyncResult, PatchPlan, VerifiedReads

GOVERNANCE_SYNC_MARKER = "last_governance_sync"


def run_governance_sync(
    config: OverseerConfig,
    repo_root: Path,
    adapter: VcsAdapter,
    runner: CommandRunner,
    *,
    dry_run: bool = True,
    emit,
) -> GovernanceSyncResult:
    """Execute governance-sync; default dry-run is inert (§7)."""
    docs_dir = repo_root / config.repo.root_relative_docs
    handover_path = docs_dir / config.docs.handover
    roadmap_path = docs_dir / config.docs.roadmap

    for path in (handover_path, roadmap_path):
        if not path.is_file():
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

    reads = perform_verified_reads(config, adapter, runner)
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
        return GovernanceSyncResult(
            exit_code=0,
            dry_run=dry_run,
            reads=reads,
            drift=drift,
            plan=None,
            committed=False,
            commit_sha=None,
            messages=("aligned",),
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

    patched_handover, handover_sections = build_handover_patches(
        handover_text,
        reads,
        drift,
        realign_summary=realign_summary,
    )
    patched_roadmap, roadmap_sections = build_roadmap_patches(
        roadmap_text,
        reads,
        drift,
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
    if realign_summary:
        emit(realign_summary)
    if dry_run:
        emit("dry-run: no writes, commits, or realign apply")
        if pr_url:
            emit(f"docs-only PR URL (operator-gated): {pr_url}")
        return GovernanceSyncResult(
            exit_code=0,
            dry_run=True,
            reads=reads,
            drift=drift,
            plan=plan,
            committed=False,
            commit_sha=None,
            messages=("dry-run plan",),
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
) -> GovernanceSyncResult:
    """Apply patches, optional realign, commit, and push on a feature branch."""
    original_handover = handover_path.read_text(encoding="utf-8")
    original_roadmap = roadmap_path.read_text(encoding="utf-8")

    try:
        atomic_write_text(handover_path, plan.handover_text)
        atomic_write_text(roadmap_path, plan.roadmap_text)
    except WriteFailure as exc:
        atomic_write_text(handover_path, original_handover)
        atomic_write_text(roadmap_path, original_roadmap)
        emit(f"write failed: {exc}")
        return GovernanceSyncResult(
            exit_code=5,
            dry_run=False,
            reads=reads,
            drift=drift,
            plan=plan,
            committed=False,
            commit_sha=None,
            messages=(str(exc),),
        )

    realign_summary, realign_error = execute_realign_guard(
        config,
        adapter,
        reads,
        drift,
        dry_run=False,
    )
    if realign_error:
        atomic_write_text(handover_path, original_handover)
        atomic_write_text(roadmap_path, original_roadmap)
        emit(f"realign failed: {realign_error}")
        return GovernanceSyncResult(
            exit_code=2,
            dry_run=False,
            reads=reads,
            drift=drift,
            plan=plan,
            committed=False,
            commit_sha=None,
            messages=(realign_error,),
            error_command=realign_error,
        )

    _write_sync_marker(repo_root)

    rel_handover = _repo_relative(repo_root, handover_path)
    rel_roadmap = _repo_relative(repo_root, roadmap_path)
    checkout = _ensure_feature_branch(adapter, runner, repo_root, config, plan.feature_branch)
    if checkout is not None:
        atomic_write_text(handover_path, original_handover)
        atomic_write_text(roadmap_path, original_roadmap)
        emit(checkout)
        return GovernanceSyncResult(
            exit_code=2,
            dry_run=False,
            reads=reads,
            drift=drift,
            plan=plan,
            committed=False,
            commit_sha=None,
            messages=(checkout,),
            error_command=checkout,
        )

    commit = adapter.commit_feature(
        branch=plan.feature_branch,
        message=plan.commit_message,
        paths=[rel_handover, rel_roadmap],
    )
    if isinstance(commit, (ReadError, WriteError)):
        atomic_write_text(handover_path, original_handover)
        atomic_write_text(roadmap_path, original_roadmap)
        cmd = commit.command if hasattr(commit, "command") else "commit_feature"
        emit(str(commit))
        return GovernanceSyncResult(
            exit_code=2,
            dry_run=False,
            reads=reads,
            drift=drift,
            plan=plan,
            committed=False,
            commit_sha=None,
            messages=(str(commit),),
            error_command=cmd,
        )

    push_error = _push_feature_branch(runner, repo_root, config, plan.feature_branch)
    if push_error:
        emit(push_error)

    if plan.pr_url:
        emit(f"docs-only PR URL (operator-gated — do not auto-open): {plan.pr_url}")

    return GovernanceSyncResult(
        exit_code=0,
        dry_run=False,
        reads=reads,
        drift=drift,
        plan=plan,
        committed=commit.committed,
        commit_sha=commit.sha,
        messages=("applied",),
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


def _write_sync_marker(repo_root: Path) -> None:
    marker = repo_root / ".overseer" / GOVERNANCE_SYNC_MARKER
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    atomic_write_text(marker, stamp + "\n")


def _repo_relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _ensure_feature_branch(
    adapter: VcsAdapter,
    runner: CommandRunner,
    repo_root: Path,
    config: OverseerConfig,
    branch: str,
) -> str | None:
    root = str(repo_root)
    if config.vcs.regime == "muse-only":
        create_cmd = f"muse -C {quote_arg(root)} checkout -b {quote_arg(branch)}"
        create = runner.run(create_cmd, cwd=root)
        if create.ok:
            return None
        switch_cmd = f"muse -C {quote_arg(root)} checkout {quote_arg(branch)}"
        switch = runner.run(switch_cmd, cwd=root)
        if not switch.ok:
            return switch_cmd
        return None

    create = runner.run(
        f"git checkout -b {quote_arg(branch)}",
        cwd=root,
    )
    if create.ok:
        return None
    switch = runner.run(
        f"git checkout {quote_arg(branch)}",
        cwd=root,
    )
    if not switch.ok:
        return f"git checkout {branch}"
    return None


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

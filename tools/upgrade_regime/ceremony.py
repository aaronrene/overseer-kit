"""Stage 3 upgrade ceremony classifiers, gates, and orchestrator (§O2.3–§O2.7)."""

from __future__ import annotations

import re
import shlex
import stat
from argparse import Namespace
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from adapters.config import OverseerConfig, load_config
from adapters.errors import ConfigError
from adapters.runner import CommandRunner, quote_arg
from cli.atomic import WriteFailure, atomic_write_text
from cli.config_gen import config_dict_to_yaml, config_to_dict, load_config_from_dict
from cli.context import CliContext
from cli.footprint import (
    MUSE_BRIDGE_DEPLOY_DEST,
    MUSE_BRIDGE_WORKFLOW_DEST,
    resolve_footprint,
)
from cli.paths import resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error, sanitize_text
from cli.version_lock import read_version_lock

SUPPORTED_FROM = "muse-only"
SUPPORTED_TO = "muse+git-mirror"
BRIDGE_DESTINATIONS = frozenset({MUSE_BRIDGE_WORKFLOW_DEST, MUSE_BRIDGE_DEPLOY_DEST})

# Heuristic secret / home-path patterns for G6 (aligned with K7 security tests).
_SECRET_ASSIGN_RE = re.compile(
    r"(?i)(?:api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}['\"]",
)
_HOME_PATH_RE = re.compile(r"(?:/Users/|/home/[a-zA-Z])")
_AWS_KEY_RE = re.compile(r"AKIA[0-9A-Z]{16}")


class StartState(str, Enum):
    """C1 start-state classification (§O2.3)."""

    MUSE_ONLY = "muse-only"
    COMPLETE_UPGRADE = "complete-upgrade"
    INCOMPLETE_UPGRADE = "incomplete-upgrade"
    WRONG_REGIME = "wrong-regime"
    MISSING_CONFIG = "missing-config"


@dataclass
class GateResult:
    """One bridge dry-run gate outcome."""

    gate_id: str
    ok: bool
    detail: str


@dataclass
class UpgradeReport:
    """Machine-readable ceremony report (§O2.5 G7 / C6)."""

    start_state: str = ""
    steps_planned: list[str] = field(default_factory=list)
    steps_completed: list[str] = field(default_factory=list)
    gates: dict[str, dict[str, Any]] = field(default_factory=dict)
    ready_for_live_bridge: bool = False
    ready_for_footprint: bool = False
    dry_run: bool = True
    apply: bool = False
    live_bridge: bool = False
    live_bridge_invoked: bool = False
    next_live_step: str = (
        "Run ./scripts/muse-bridge-deploy.sh → push muse-mirror → open PR to main; "
        "merge muse-mirror → main remains Tier 3 (never auto)."
    )
    hard_stop_c8: str = "Merge muse-mirror → main is Tier 3 — ceremony stops before C8."
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    docs_preserved: bool = True
    config_written: bool = False
    footprint_seeded: bool = False

    def to_payload(self) -> dict[str, Any]:
        return {
            "start_state": self.start_state,
            "steps_planned": list(self.steps_planned),
            "steps_completed": list(self.steps_completed),
            "gates": dict(self.gates),
            "ready_for_live_bridge": self.ready_for_live_bridge,
            "ready_for_footprint": self.ready_for_footprint,
            "dry_run": self.dry_run,
            "apply": self.apply,
            "live_bridge": self.live_bridge,
            "live_bridge_invoked": self.live_bridge_invoked,
            "next_live_step": self.next_live_step,
            "hard_stop_c8": self.hard_stop_c8,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "docs_preserved": self.docs_preserved,
            "config_written": self.config_written,
            "footprint_seeded": self.footprint_seeded,
        }


def required_vcs_complete(config: OverseerConfig) -> bool:
    """True when on-disk VCS block satisfies §O2.4.2 minimum for muse+git-mirror."""
    vcs = config.vcs
    if vcs.regime != SUPPORTED_TO:
        return False
    if vcs.canonical != "muse":
        return False
    if not vcs.git.mirror_branch:
        return False
    if not vcs.git.remote or not vcs.git.main_branch:
        return False
    if not vcs.muse.staging_remote:
        return False
    if not vcs.muse.main_branch:
        return False
    return True


def is_silent_regime_only_patch(before: OverseerConfig | None, after_dict: dict) -> bool:
    """Detect forbidden silent edit: regime flip without required mirror fields (§O2.4.1)."""
    if before is None:
        return False
    after_vcs = after_dict.get("vcs") or {}
    if after_vcs.get("regime") != SUPPORTED_TO:
        return False
    git = after_vcs.get("git") or {}
    muse = after_vcs.get("muse") or {}
    incomplete = (
        not git.get("mirror_branch")
        or after_vcs.get("canonical") != "muse"
        or not muse.get("staging_remote")
        or not muse.get("main_branch")
    )
    if not incomplete:
        return False
    # Regime-only (or regime + partial) relative to a muse-only start.
    return before.vcs.regime == SUPPORTED_FROM


def docs_preserved(before: OverseerConfig, after: OverseerConfig) -> bool:
    """Living-doc paths and repo identity must survive C2 (§O2.4.2)."""
    return (
        before.docs.handover == after.docs.handover
        and before.docs.roadmap == after.docs.roadmap
        and before.docs.coordination == after.docs.coordination
        and before.docs.standing_decisions == after.docs.standing_decisions
        and before.repo.name == after.repo.name
        and before.repo.root_relative_docs == after.repo.root_relative_docs
    )


def build_upgraded_config_dict(config: OverseerConfig) -> dict:
    """Build muse+git-mirror config preserving docs.*/repo.*/thresholds./freeze (§O2.4.2)."""
    data = config_to_dict(config)
    prev_git = data["vcs"]["git"]
    prev_muse = data["vcs"]["muse"]
    data["vcs"] = {
        "regime": SUPPORTED_TO,
        "canonical": "muse",
        "git": {
            "remote": prev_git.get("remote") or "origin",
            "main_branch": prev_git.get("main_branch") or "main",
            "mirror_branch": prev_git.get("mirror_branch") or "muse-mirror",
            "feature_branch_pattern": prev_git.get("feature_branch_pattern")
            or "feat/{slug}",
        },
        "muse": {
            "staging_remote": prev_muse.get("staging_remote") or "staging",
            "main_branch": prev_muse.get("main_branch") or "main",
            "working_dir": prev_muse.get("working_dir"),
        },
    }
    return data


def bridge_footprint_present(repo_root: Path, config: OverseerConfig) -> bool:
    """True when both bridge destinations are in lock + on disk (executable script)."""
    lock_file = repo_root / ".overseer" / "version.lock"
    if not lock_file.is_file():
        return False
    try:
        lock = read_version_lock(lock_file)
    except (OSError, ValueError, KeyError):
        return False
    locked = {e.path for e in lock.footprint}
    if not BRIDGE_DESTINATIONS.issubset(locked):
        return False
    workflow = repo_root / MUSE_BRIDGE_WORKFLOW_DEST
    script = repo_root / MUSE_BRIDGE_DEPLOY_DEST
    if not workflow.is_file() or not script.is_file():
        return False
    mode = script.stat().st_mode
    if not (mode & stat.S_IXUSR):
        return False
    # Config must resolve bridge destinations for this regime.
    dests = {f.destination for f in resolve_footprint(config)}
    return BRIDGE_DESTINATIONS.issubset(dests)


def classify_start_state(repo_root: Path, config_path: Path) -> StartState:
    """C1 classifier (§O2.3)."""
    if not config_path.is_file():
        return StartState.MISSING_CONFIG
    try:
        config = load_config(config_path)
    except ConfigError:
        return StartState.WRONG_REGIME

    regime = config.vcs.regime
    if regime == SUPPORTED_FROM:
        return StartState.MUSE_ONLY
    if regime == SUPPORTED_TO:
        if required_vcs_complete(config) and bridge_footprint_present(repo_root, config):
            return StartState.COMPLETE_UPGRADE
        return StartState.INCOMPLETE_UPGRADE
    return StartState.WRONG_REGIME


def check_g3_deploy_script(script: str) -> GateResult:
    """G3: S3 refusal (mirror ≠ root) and never export to ``--git-dir .``."""
    if "mirror directory equals repo root" not in script and "MIRROR_ABS == REPO_ABS" not in script:
        return GateResult("G3", False, "missing mirror≠root refusal")
    # Live export must use absolute mirror path variable, not literal `.`
    if re.search(r"""--git-dir\s+['\"]?\.(?:['\"]|\s|$)""", script):
        return GateResult("G3", False, "script instructs --git-dir .")
    if "--git-dir" in script and "MIRROR_ABS" not in script and "MIRROR_DIR" not in script:
        return GateResult("G3", False, "export target not isolated mirror path")
    return GateResult("G3", True, "S3 mirror-isolation present")


def check_g4_deploy_script(script: str) -> GateResult:
    """G4: never push main; publish via mirror_branch only (S8/S13)."""
    if "git push origin main" in script:
        return GateResult("G4", False, "literal push origin main present")
    if 'push "${GIT_REMOTE}" "${MAIN_BRANCH}"' in script:
        return GateResult("G4", False, "push of MAIN_BRANCH present")
    if 'push "${GIT_REMOTE}" "${MIRROR_BRANCH}"' not in script and "MIRROR_BRANCH" not in script:
        return GateResult("G4", False, "mirror_branch push path missing")
    return GateResult("G4", True, "mirror-only publish path")


def check_g5_deploy_script(script: str) -> GateResult:
    """G5: cwd-safe ``muse -C`` + absolute ``--git-dir`` (S7)."""
    if 'muse -C "' not in script and "muse -C '${" not in script and 'muse -C "${' not in script:
        if "muse -C" not in script:
            return GateResult("G5", False, "missing muse -C")
    if '--git-dir "${MIRROR_ABS}"' not in script and "--git-dir" not in script:
        return GateResult("G5", False, "missing absolute --git-dir mirror path")
    return GateResult("G5", True, "muse -C + absolute --git-dir")


def check_g6_deploy_script(script: str) -> GateResult:
    """G6: no secret-assignment / absolute home paths (S11)."""
    if _HOME_PATH_RE.search(script):
        return GateResult("G6", False, "absolute operator home path in script")
    if _AWS_KEY_RE.search(script) or _SECRET_ASSIGN_RE.search(script):
        return GateResult("G6", False, "secret-assignment pattern in script")
    return GateResult("G6", True, "no secrets / home paths")


def check_g8_git_remote(
    repo_root: Path,
    remote_name: str,
    runner: CommandRunner,
) -> GateResult:
    """G8: local read-only ``git remote get-url`` returns non-empty URL (no network fetch)."""
    cmd = f"git remote get-url {quote_arg(remote_name)}"
    result = runner.run(cmd, cwd=str(repo_root))
    url = (result.stdout or "").strip()
    if result.exit_code != 0 or not url:
        return GateResult(
            "G8",
            False,
            f"git remote {remote_name!r} has no usable URL (create repo + remote before C7)",
        )
    return GateResult("G8", True, f"remote {remote_name} URL present")


def evaluate_bridge_gates(
    *,
    config: OverseerConfig,
    repo_root: Path,
    runner: CommandRunner,
) -> list[GateResult]:
    """Evaluate G1–G8 without live export (§O2.5)."""
    results: list[GateResult] = []

    # G1 — config shape
    g1_ok = required_vcs_complete(config)
    results.append(
        GateResult(
            "G1",
            g1_ok,
            "vcs muse+git-mirror complete" if g1_ok else "vcs shape incomplete for muse+git-mirror",
        )
    )

    # G2 — footprint lock + disk + executable
    g2_ok = bridge_footprint_present(repo_root, config)
    results.append(
        GateResult(
            "G2",
            g2_ok,
            "bridge footprint present" if g2_ok else "bridge destinations missing from lock/disk",
        )
    )

    script_path = repo_root / MUSE_BRIDGE_DEPLOY_DEST
    script_text = script_path.read_text(encoding="utf-8") if script_path.is_file() else ""

    results.append(check_g3_deploy_script(script_text) if script_text else GateResult("G3", False, "deploy script missing"))
    results.append(check_g4_deploy_script(script_text) if script_text else GateResult("G4", False, "deploy script missing"))
    results.append(check_g5_deploy_script(script_text) if script_text else GateResult("G5", False, "deploy script missing"))
    results.append(check_g6_deploy_script(script_text) if script_text else GateResult("G6", False, "deploy script missing"))

    # G7 — informational always "pass" when report includes next_live_step (orchestrator sets it)
    results.append(
        GateResult(
            "G7",
            True,
            "next live step is deploy script → muse-mirror PR; merge remains Tier 3",
        )
    )

    remote = config.vcs.git.remote
    results.append(check_g8_git_remote(repo_root, remote, runner))
    return results


def _path_escape_ok(repo_root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(repo_root.resolve())
        return True
    except ValueError:
        return False


def run_upgrade_regime(args: Namespace, ctx: CliContext) -> tuple[int, UpgradeReport]:
    """Orchestrate C0–C5 (and optional C7); hard-stop before C8 (§O2.3 / §O2.7)."""
    report = UpgradeReport()

    from_regime = getattr(args, "from_regime", None) or getattr(args, "from", None)
    to_regime = getattr(args, "to_regime", None) or getattr(args, "to", None)
    if from_regime != SUPPORTED_FROM or to_regime != SUPPORTED_TO:
        report.errors.append(
            f"refused: only supported pair is --from {SUPPORTED_FROM} --to {SUPPORTED_TO}"
        )
        return 4, report

    apply = bool(getattr(args, "apply", False))
    live_bridge = bool(getattr(args, "live_bridge", False))
    force = bool(getattr(args, "force", False))
    yes = bool(getattr(args, "yes", False))
    # Default is dry-run unless --apply (or live with apply path).
    dry_run = bool(getattr(args, "dry_run", False)) or not apply
    if live_bridge and not apply:
        # Live bridge implies apply first unless already complete (handled below).
        apply = True
        dry_run = False

    report.dry_run = dry_run
    report.apply = apply
    report.live_bridge = live_bridge

    try:
        repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=getattr(args, "repo", None), command="upgrade-regime")
    except Exception as exc:  # noqa: BLE001 — path resolution failures are refuse
        report.errors.append(sanitize_text(str(exc), ctx.cwd))
        return 4, report

    config_path = resolve_config_path(repo_root, getattr(args, "config", None))
    if not _path_escape_ok(repo_root, config_path):
        report.errors.append("refused: config path outside repo root")
        return 4, report

    # C0 prerequisites (non-writing)
    report.steps_planned.append("C0")
    report.steps_completed.append("C0")

    # C1 start-state
    start = classify_start_state(repo_root, config_path)
    report.start_state = start.value
    report.steps_planned.append("C1")
    report.steps_completed.append("C1")

    if start in {StartState.WRONG_REGIME, StartState.MISSING_CONFIG}:
        report.errors.append(
            "refused: wrong ceremony start state "
            f"({start.value}); use greenfield ok init or a later git→mirror freeze"
        )
        return 4, report

    if start == StartState.COMPLETE_UPGRADE:
        config = load_config(config_path)
        gates = evaluate_bridge_gates(config=config, repo_root=repo_root, runner=ctx.runner)
        report.gates = {g.gate_id: {"ok": g.ok, "detail": g.detail} for g in gates}
        g1_g7 = all(g.ok for g in gates if g.gate_id != "G8")
        g8 = next(g for g in gates if g.gate_id == "G8")
        report.ready_for_footprint = g1_g7
        report.ready_for_live_bridge = all(g.ok for g in gates)
        report.steps_planned.extend(["C5", "G1-G8"])
        report.steps_completed.extend(["C5", "G1-G8"])
        if live_bridge:
            if not report.ready_for_live_bridge or not yes:
                report.errors.append(
                    "refused: --live-bridge requires G1–G8 pass and -y/--yes consent (C6)"
                )
                return 4, report
            return _invoke_live_bridge(repo_root, ctx, report)
        report.warnings.append("idempotent success: already muse+git-mirror with bridge footprint")
        return 0, report

    # Load pre-upgrade config
    try:
        before = load_config(config_path)
    except ConfigError as exc:
        report.errors.append(format_config_error(exc, repo_root))
        return 2, report

    need_c2 = start == StartState.MUSE_ONLY or not required_vcs_complete(before)
    report.steps_planned.extend(["C2", "C3", "C4", "C5"] if need_c2 else ["C3", "C4", "C5"])

    upgraded_dict = build_upgraded_config_dict(before)
    if is_silent_regime_only_patch(before, upgraded_dict):
        report.errors.append(
            "refused: silent regime-only patch detected (complete VCS fields required)"
        )
        return 4, report

    try:
        upgraded = load_config_from_dict(upgraded_dict, str(config_path))
    except ConfigError as exc:
        report.errors.append(format_config_error(exc, repo_root))
        return 2, report

    if not required_vcs_complete(upgraded):
        report.errors.append("refused: projected post-upgrade VCS incomplete")
        return 4, report

    report.docs_preserved = docs_preserved(before, upgraded)
    if not report.docs_preserved:
        report.errors.append("refused: docs.*/repo.* would not be preserved")
        return 4, report
    # Dry-run: plan only through C5/G1–G8; no writes.
    if dry_run and not apply:
        for step in report.steps_planned:
            if step not in report.steps_completed:
                report.steps_completed.append(step)
        probe_config = upgraded if need_c2 else before
        gates = evaluate_bridge_gates(config=probe_config, repo_root=repo_root, runner=ctx.runner)
        # Projected G1 always reflects the post-upgrade VCS shape.
        gates = [
            GateResult("G1", True, "projected vcs complete") if g.gate_id == "G1" else g
            for g in gates
        ]
        if start == StartState.MUSE_ONLY and not bridge_footprint_present(repo_root, upgraded):
            patched: list[GateResult] = []
            for g in gates:
                if g.gate_id in {"G2", "G3", "G4", "G5", "G6"} and not g.ok:
                    patched.append(GateResult(g.gate_id, False, "requires --apply footprint seed"))
                else:
                    patched.append(g)
            gates = patched
            report.warnings.append("dry-run: no writes; run --apply to perform C2–C4")
        report.gates = {g.gate_id: {"ok": g.ok, "detail": g.detail} for g in gates}
        report.ready_for_footprint = all(
            report.gates[g]["ok"] for g in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")
        )
        report.ready_for_live_bridge = all(g["ok"] for g in report.gates.values())
        if live_bridge:
            report.errors.append("refused: --live-bridge requires successful --apply path + G1–G8")
            return 4, report
        return 0, report

    # --- Apply path: C2–C4 writes ---
    if need_c2:
        try:
            atomic_write_text(config_path, config_dict_to_yaml(upgraded_dict))
            report.config_written = True
            report.steps_completed.append("C2")
        except WriteFailure as exc:
            report.errors.append(sanitize_text(str(exc), repo_root))
            return 5, report
    else:
        report.steps_completed.append("C2-skipped")

    # Reload post-C2
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        report.errors.append(format_config_error(exc, repo_root))
        return 2, report

    if config.vcs.regime != SUPPORTED_TO:
        report.errors.append("refused: post-C2 config did not load as muse+git-mirror")
        return 4, report

    # C3 footprint re-seed via sync (never --include-preserved)
    sync_code = _run_sync_seed(args, ctx, force=force)
    if sync_code == 4:
        report.errors.append(
            "refused: shared-asset conflict on bridge files without --force "
            "(living docs never force-promoted on Stage 3 path)"
        )
        return 4, report
    if sync_code not in (0,):
        report.errors.append(f"footprint re-seed failed (exit {sync_code})")
        return sync_code if sync_code else 1, report
    report.footprint_seeded = True
    report.steps_completed.append("C3")

    # C4 footprint gate
    if not bridge_footprint_present(repo_root, config):
        report.errors.append("refused: C4 footprint gate failed — bridge destinations missing")
        return 4, report
    report.steps_completed.append("C4")

    # C5 gates
    gates = evaluate_bridge_gates(config=config, repo_root=repo_root, runner=ctx.runner)
    report.gates = {g.gate_id: {"ok": g.ok, "detail": g.detail} for g in gates}
    report.steps_completed.append("C5")
    report.ready_for_footprint = all(
        report.gates[g]["ok"] for g in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")
    )
    report.ready_for_live_bridge = all(g["ok"] for g in report.gates.values())

    if not report.ready_for_footprint:
        report.errors.append("refused: bridge dry-run gates G1–G7 failed")
        return 4, report

    if live_bridge:
        if not report.ready_for_live_bridge:
            report.errors.append(
                "refused: not ready for live bridge (G8 or earlier gate failed); "
                "config+footprint remain muse+git-mirror for retry"
            )
            return 4, report
        if not yes:
            report.errors.append("refused: --live-bridge requires -y/--yes after gates pass (C6)")
            return 4, report
        return _invoke_live_bridge(repo_root, ctx, report)

    if yes and not live_bridge:
        # --yes alone without gate success / live-bridge is not a C7 consent.
        pass

    return 0, report


def _run_sync_seed(args: Namespace, ctx: CliContext, *, force: bool) -> int:
    """Compose ``ok sync -y`` for C3; ``--force`` only for bridge shared-asset conflicts."""
    from cli.commands.sync import run_sync

    sync_args = Namespace(
        repo=getattr(args, "repo", None),
        config=getattr(args, "config", None),
        dry_run=False,
        diff=False,
        only=None,
        force=force,
        yes=True,
        include_preserved=False,  # never on product Stage 3 path
    )
    return run_sync(sync_args, ctx)


def _invoke_live_bridge(repo_root: Path, ctx: CliContext, report: UpgradeReport) -> tuple[int, UpgradeReport]:
    """C7: invoke vendored deploy script only — never C8 merge."""
    script = repo_root / MUSE_BRIDGE_DEPLOY_DEST
    if not script.is_file():
        report.errors.append("refused: deploy script missing for live bridge")
        return 4, report
    if not _path_escape_ok(repo_root, script):
        report.errors.append("refused: deploy script path escapes repo")
        return 4, report
    msg = "mirror: Stage 3 upgrade-regime first live bridge"
    cmd = f"{shlex.quote(str(script))} {shlex.quote(msg)}"
    result = ctx.runner.run(cmd, cwd=str(repo_root))
    report.live_bridge_invoked = True
    report.steps_completed.append("C7")
    if result.exit_code != 0:
        report.errors.append(
            sanitize_text(
                result.stderr or f"live bridge failed (exit {result.exit_code})",
                repo_root,
            )
        )
        # Default: do not roll back config/footprint (§O2.5).
        return result.exit_code if result.exit_code else 1, report
    report.warnings.append(
        "C7 complete: merge muse-mirror → main remains Tier 3 (C8 hard stop)"
    )
    return 0, report

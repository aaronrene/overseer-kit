"""Post-merge land closeout probe (§PMHF.5) — never merges, never writes docs.

Composes the GFG freshness probe (D1/D2/marker authority) with the handover
``land-phase`` posture (§PMHF.4) to resolve one of the frozen states:
``not_applicable`` | ``land_a_in_progress`` | ``post_merge_incomplete`` |
``land_b_in_progress`` | ``complete`` | ``unreadable``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from adapters.base import VcsAdapter
from adapters.config import OverseerConfig, resolve_lane_docs
from adapters.factory import create_adapter
from adapters.runner import CommandRunner, SubprocessRunner
from cli.docs_paths import lane_living_doc_abs
from cli.version_lock import LockError, lock_path, read_version_lock
from tools.governance_freshness import (
    GovernanceFreshnessReport,
    check_governance_freshness,
)
from tools.governance_hygiene.next_regen import (
    LAND_B_REMEDIATION,
    LAND_PHASE_A,
    LAND_PHASE_B,
    LAND_PHASE_UNREADABLE,
    extract_land_id,
    extract_paste_pr_number,
    land_queue_conflict,
    resolve_land_phase,
)

STATE_NOT_APPLICABLE = "not_applicable"
STATE_LAND_A_IN_PROGRESS = "land_a_in_progress"
STATE_POST_MERGE_INCOMPLETE = "post_merge_incomplete"
STATE_LAND_B_IN_PROGRESS = "land_b_in_progress"
STATE_COMPLETE = "complete"
STATE_UNREADABLE = "unreadable"

CONFLICT_TOKEN = "land_phase_conflicts_queue_done"
LAND_B_FINISH_REMEDIATION = (
    "finish land-b: ok governance-sync --dry-run then apply; "
    "clear land-phase once NEXT matches merged main"
)


@dataclass(frozen=True)
class LandCloseoutReport:
    """Result of a land-closeout probe (§PMHF.5)."""

    state: str
    message: str
    remediation: str | None
    land_phase: str | None  # land-a | land-b | None
    freshness_ok: bool
    d1: str | None
    optional_pr_merged: bool | None  # None = not probed

    @property
    def ok(self) -> bool:
        """Status-floor semantics: mid-land wait must not fail the tree (§PMHF.5)."""
        return self.state in {
            STATE_NOT_APPLICABLE,
            STATE_LAND_A_IN_PROGRESS,
            STATE_COMPLETE,
        }


def land_complete(report: LandCloseoutReport) -> bool:
    """§PMHF.3.3 — stricter than ``report.ok``; ``land_a_in_progress`` is never complete."""
    return report.freshness_ok and (
        report.state == STATE_COMPLETE
        or (report.state == STATE_NOT_APPLICABLE and report.freshness_ok)
    )


def check_land_closeout(
    config: OverseerConfig,
    repo_root: Path,
    *,
    adapter: VcsAdapter | None = None,
    runner: CommandRunner | None = None,
    probe_merged_pr: bool = False,
    freshness: GovernanceFreshnessReport | None = None,
) -> LandCloseoutReport:
    """Resolve land closeout per §PMHF.5.2. Reuses the GFG probe; no re-derivation.

    ``freshness`` may be injected by callers (``ok status``) that already ran the
    GFG probe. ``probe_merged_pr`` is the only path that may invoke ``gh``
    (§PMHF.5.3); it is skipped for ``muse-only`` regardless of the flag.
    """
    try:
        lock_file = lock_path(repo_root)
        if not lock_file.is_file():
            return LandCloseoutReport(
                state=STATE_NOT_APPLICABLE,
                message="not initialized — no land closeout obligation yet",
                remediation=None,
                land_phase=None,
                freshness_ok=True,
                d1=None,
                optional_pr_merged=None,
            )
        read_version_lock(lock_file)
    except LockError as exc:
        return _unreadable(f"version.lock unreadable: {exc}", remediation="ok sync")
    except OSError as exc:
        return _unreadable(f"could not load install state: {exc}", remediation="ok sync")

    active_runner = runner or SubprocessRunner()
    if freshness is None:
        active_adapter = adapter or create_adapter(config, repo_root, runner=active_runner)
        freshness = check_governance_freshness(
            config,
            repo_root,
            adapter=active_adapter,
            runner=active_runner,
        )

    if freshness.state == "unreadable":
        # §PMHF.5.2 step 3 / R2-M2: never mask unreadable as post_merge_incomplete.
        return _unreadable(
            f"governance freshness unreadable — failing closed: {freshness.message}",
            remediation=freshness.remediation,
            freshness_ok=False,
            d1=freshness.d1,
        )

    try:
        handover_text, roadmap_text = _load_default_lane_docs(config, repo_root)
    except OSError as exc:
        return _unreadable(
            f"governance docs unreadable: {exc}",
            remediation="ok governance-sync --dry-run",
            freshness_ok=freshness.ok,
            d1=freshness.d1,
        )

    land_phase = resolve_land_phase(handover_text)
    if land_phase == LAND_PHASE_UNREADABLE:
        return _unreadable(
            "land-phase unreadable — unknown marker value or conflicting "
            "land-a/land-b vocabulary in the paste fence",
            remediation="fix the handover NEXT marker land-phase attribute",
            freshness_ok=freshness.ok,
            d1=freshness.d1,
        )

    main_branch = config.vcs.git.main_branch or "main"
    if land_phase == LAND_PHASE_A:
        land_id = extract_land_id(handover_text)
        if land_id and land_queue_conflict(roadmap_text, land_id, main_branch=main_branch):
            # §PMHF.3.3 frozen check: queue row DONE/MERGED while handover says land-a.
            return LandCloseoutReport(
                state=STATE_UNREADABLE,
                message=(
                    f"{CONFLICT_TOKEN} — matching land queue row is DONE/MERGED "
                    "while handover land-phase=land-a"
                ),
                remediation=LAND_B_REMEDIATION,
                land_phase=LAND_PHASE_A,
                freshness_ok=freshness.ok,
                d1=freshness.d1,
                optional_pr_merged=None,
            )

    if land_phase is None:
        return LandCloseoutReport(
            state=STATE_NOT_APPLICABLE,
            message="no land posture on NEXT — closeout not applicable",
            remediation=None,
            land_phase=None,
            freshness_ok=freshness.ok,
            d1=freshness.d1,
            optional_pr_merged=None,
        )

    optional_pr_merged: bool | None = None
    if probe_merged_pr and config.vcs.regime != "muse-only":
        optional_pr_merged = _probe_merged_pr(handover_text, active_runner)

    if land_phase == LAND_PHASE_A:
        if (
            freshness.d1 == "drifted"
            or freshness.state in {"drifted", "stale_marker"}
            or optional_pr_merged is True
        ):
            return LandCloseoutReport(
                state=STATE_POST_MERGE_INCOMPLETE,
                message=(
                    "merge reflected on main but handover NEXT still says land-a "
                    "(wait-for-merge)"
                ),
                remediation=LAND_B_REMEDIATION,
                land_phase=LAND_PHASE_A,
                freshness_ok=freshness.ok,
                d1=freshness.d1,
                optional_pr_merged=optional_pr_merged,
            )
        return LandCloseoutReport(
            state=STATE_LAND_A_IN_PROGRESS,
            message="land-a in progress — waiting for Tier 3 merge; main tip still aligned",
            remediation=None,
            land_phase=LAND_PHASE_A,
            freshness_ok=freshness.ok,
            d1=freshness.d1,
            optional_pr_merged=optional_pr_merged,
        )

    # land-b
    if not freshness.ok or freshness.d1 == "drifted":
        return LandCloseoutReport(
            state=STATE_LAND_B_IN_PROGRESS,
            message="land-b in progress — living docs not yet synced to merged main",
            remediation=LAND_B_FINISH_REMEDIATION,
            land_phase=LAND_PHASE_B,
            freshness_ok=freshness.ok,
            d1=freshness.d1,
            optional_pr_merged=optional_pr_merged,
        )
    return LandCloseoutReport(
        state=STATE_COMPLETE,
        message="land closeout complete — freshness ok and land-b posture satisfied",
        remediation=None,
        land_phase=LAND_PHASE_B,
        freshness_ok=freshness.ok,
        d1=freshness.d1,
        optional_pr_merged=optional_pr_merged,
    )


def _unreadable(
    message: str,
    *,
    remediation: str | None,
    freshness_ok: bool = False,
    d1: str | None = None,
) -> LandCloseoutReport:
    return LandCloseoutReport(
        state=STATE_UNREADABLE,
        message=message,
        remediation=remediation,
        land_phase=None,
        freshness_ok=freshness_ok,
        d1=d1,
        optional_pr_merged=None,
    )


def _probe_merged_pr(handover_text: str, runner: CommandRunner) -> bool | None:
    """§PMHF.5.3 optional enrichment; gh missing/failed → None (never fail open)."""
    number = extract_paste_pr_number(handover_text)
    if number is None:
        return None
    command = f"gh pr view {number} --json state,mergedAt"
    result = runner.run(command)
    if not result.ok:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    state = str(payload.get("state", "")).strip().upper()
    if state == "MERGED" or payload.get("mergedAt"):
        return True
    return False


def _load_default_lane_docs(config: OverseerConfig, repo_root: Path) -> tuple[str, str]:
    lane = config.docs.default_lane if config.docs.lanes is not None else None
    lane_docs = resolve_lane_docs(config, lane)
    handover_path = lane_living_doc_abs(repo_root, config, lane_docs, lane_docs.handover)
    roadmap_path = lane_living_doc_abs(repo_root, config, lane_docs, lane_docs.roadmap)
    handover = handover_path.read_text(encoding="utf-8") if handover_path.is_file() else ""
    roadmap = roadmap_path.read_text(encoding="utf-8") if roadmap_path.is_file() else ""
    return handover, roadmap


def land_closeout_payload(report: LandCloseoutReport) -> dict:
    """JSON payload shape shared by ``ok status`` and ``ok land-closeout`` (§PMHF.6.1)."""
    return {
        "state": report.state,
        "ok": report.ok,
        "message": report.message,
        "remediation": report.remediation,
        "land_phase": report.land_phase,
        "freshness_ok": report.freshness_ok,
        "d1": report.d1,
        "optional_pr_merged": report.optional_pr_merged,
    }

"""Governance freshness probe — D1/D2 + marker; skips R4/gh (§GFG.4)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.base import VcsAdapter
from adapters.config import OverseerConfig, resolve_lane_docs
from adapters.errors import ReadError
from adapters.factory import create_adapter
from adapters.runner import CommandRunner, SubprocessRunner
from cli.docs_paths import lane_living_doc_abs
from cli.version_lock import LockError, lock_path, read_version_lock
from tools.governance_hygiene.drift import detect_drift
from tools.governance_hygiene.types import VerifiedReads

GOVERNANCE_SYNC_MARKER = "last_governance_sync"
REMEDIATION_DRY_RUN = (
    "ok governance-sync --dry-run then apply when the plan is correct "
    "(ok governance-sync without dry-run / explicit apply path)"
)
REMEDIATION_RESTAMP = "ok governance-sync --dry-run"


@dataclass(frozen=True)
class SyncMarker:
    """Parsed ``.overseer/last_governance_sync`` (§GFG.5.2)."""

    timestamp: str
    r1: str | None  # None = absent key; "" = present empty
    r3: str | None
    legacy: bool  # True when tip fields absent (timestamp-only)


@dataclass(frozen=True)
class GovernanceFreshnessReport:
    """Result of a governance freshness probe (§GFG.4)."""

    state: str  # ok | drifted | stale_marker | unreadable | not_applicable
    message: str
    remediation: str | None
    d1: str | None = None
    d2: str | None = None
    marker_present: bool = False
    marker_r1: str | None = None
    actual_r1: str | None = None

    @property
    def ok(self) -> bool:
        return self.state in {"ok", "not_applicable"}


def parse_sync_marker(text: str) -> SyncMarker | None:
    """Parse enriched or legacy marker body; empty input → None."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    timestamp = lines[0]
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        fields[key.strip().lower()] = value.strip()
    has_tip_key = "r1" in fields or "r3" in fields
    return SyncMarker(
        timestamp=timestamp,
        r1=fields.get("r1") if "r1" in fields else None,
        r3=fields.get("r3") if "r3" in fields else None,
        legacy=not has_tip_key,
    )


def check_governance_freshness(
    config: OverseerConfig,
    repo_root: Path,
    *,
    adapter: VcsAdapter | None = None,
    runner: CommandRunner | None = None,
) -> GovernanceFreshnessReport:
    """Resolve freshness from D1/D2 + marker; never calls ``gh`` (§GFG.4.1)."""
    try:
        lock_file = lock_path(repo_root)
        if not lock_file.is_file():
            return GovernanceFreshnessReport(
                state="not_applicable",
                message="not initialized — no freshness obligation yet",
                remediation=None,
            )
        read_version_lock(lock_file)
    except LockError as exc:
        return GovernanceFreshnessReport(
            state="unreadable",
            message=f"version.lock unreadable: {exc}",
            remediation="ok sync",
        )
    except OSError as exc:
        return GovernanceFreshnessReport(
            state="unreadable",
            message=f"could not load install state: {exc}",
            remediation="ok sync",
        )

    active_runner = runner or SubprocessRunner()
    active_adapter = adapter or create_adapter(config, repo_root, runner=active_runner)

    reads_or_fail = _perform_freshness_reads(config, active_adapter)
    if isinstance(reads_or_fail, str):
        return GovernanceFreshnessReport(
            state="unreadable",
            message=reads_or_fail,
            remediation=REMEDIATION_DRY_RUN,
        )
    reads = reads_or_fail

    try:
        handover_text, roadmap_text = _load_default_lane_docs(config, repo_root)
    except OSError as exc:
        return GovernanceFreshnessReport(
            state="unreadable",
            message=f"governance docs unreadable: {exc}",
            remediation=REMEDIATION_DRY_RUN,
            actual_r1=reads.r1_github_main_sha,
        )

    drift = detect_drift(reads, handover_text, roadmap_text)
    d1 = drift.d1_handover_vs_git
    d2 = drift.d2_anchor_vs_canonical

    if d1 == "unreadable" or d2 == "unreadable":
        return GovernanceFreshnessReport(
            state="unreadable",
            message="D1/D2 unreadable — failing closed",
            remediation=REMEDIATION_DRY_RUN,
            d1=d1,
            d2=d2,
            actual_r1=reads.r1_github_main_sha,
        )

    if d1 == "drifted" or d2 == "drifted":
        which = "D1" if d1 == "drifted" else "D2"
        if d1 == "drifted" and d2 == "drifted":
            which = "D1/D2"
        return GovernanceFreshnessReport(
            state="drifted",
            message=f"{which} drifted — handover/main freshness out of date",
            remediation=REMEDIATION_DRY_RUN,
            d1=d1,
            d2=d2,
            actual_r1=reads.r1_github_main_sha,
        )

    # D1 and D2 aligned — evaluate marker (§GFG.4.2 step 5). D3 ignored.
    marker_path = repo_root / ".overseer" / GOVERNANCE_SYNC_MARKER
    marker: SyncMarker | None = None
    if marker_path.is_file():
        try:
            marker = parse_sync_marker(marker_path.read_text(encoding="utf-8"))
        except OSError as exc:
            return GovernanceFreshnessReport(
                state="unreadable",
                message=f"marker unreadable: {exc}",
                remediation=REMEDIATION_RESTAMP,
                d1=d1,
                d2=d2,
                actual_r1=reads.r1_github_main_sha,
            )

    tip_known, tip_value, tip_field = _regime_tip(config, reads)
    marker_r1 = marker.r1 if marker is not None else None

    if marker is None:
        if tip_known:
            return GovernanceFreshnessReport(
                state="stale_marker",
                message="last_governance_sync missing after main tip is known",
                remediation=REMEDIATION_RESTAMP,
                d1=d1,
                d2=d2,
                marker_present=False,
                marker_r1=None,
                actual_r1=reads.r1_github_main_sha,
            )
        return GovernanceFreshnessReport(
            state="ok",
            message="D1/D2 aligned; tip unknown — no marker obligation",
            remediation=None,
            d1=d1,
            d2=d2,
            marker_present=False,
            actual_r1=reads.r1_github_main_sha,
        )

    if marker.legacy:
        if tip_known:
            return GovernanceFreshnessReport(
                state="stale_marker",
                message="legacy timestamp-only marker — re-stamp with enriched tip fields",
                remediation=REMEDIATION_RESTAMP,
                d1=d1,
                d2=d2,
                marker_present=True,
                marker_r1=None,
                actual_r1=reads.r1_github_main_sha,
            )
        return GovernanceFreshnessReport(
            state="ok",
            message="D1/D2 aligned; legacy marker present; tip unknown",
            remediation=None,
            d1=d1,
            d2=d2,
            marker_present=True,
            actual_r1=reads.r1_github_main_sha,
        )

    stamped = marker.r1 if tip_field == "r1" else marker.r3
    if tip_known and tip_value is not None:
        stamped_norm = (stamped or "").lower()
        if stamped_norm != tip_value.lower():
            return GovernanceFreshnessReport(
                state="stale_marker",
                message=f"main advanced since last stamp ({tip_field})",
                remediation=REMEDIATION_RESTAMP,
                d1=d1,
                d2=d2,
                marker_present=True,
                marker_r1=marker_r1,
                actual_r1=reads.r1_github_main_sha,
            )

    return GovernanceFreshnessReport(
        state="ok",
        message="D1/D2 aligned and governance sync marker matches tip",
        remediation=None,
        d1=d1,
        d2=d2,
        marker_present=True,
        marker_r1=marker_r1,
        actual_r1=reads.r1_github_main_sha,
    )


def _regime_tip(
    config: OverseerConfig,
    reads: VerifiedReads,
) -> tuple[bool, str | None, str]:
    """Return (tip_known, tip_sha, field_name) for marker comparison."""
    regime = config.vcs.regime
    if regime == "muse-only":
        tip = reads.r3_canonical_main_sha
        return tip is not None and bool(tip), tip, "r3"
    tip = reads.r1_github_main_sha
    return tip is not None and bool(tip), tip, "r1"


def _perform_freshness_reads(
    config: OverseerConfig,
    adapter: VcsAdapter,
) -> VerifiedReads | str:
    """R1/R2/R3/R5 only — empty R4; never invokes ``gh`` (§GFG.4.1)."""
    regime = config.vcs.regime

    status = adapter.status()
    if isinstance(status, ReadError):
        return f"{status.command}: {status}"

    r1_sha: str | None = None
    r1_cmd: str | None = None
    if regime in {"git-only", "muse+git-mirror"}:
        remote = config.vcs.git.remote
        main = config.vcs.git.main_branch
        r1_cmd = f"git rev-parse {remote}/{main}"
        head = adapter.read_head(f"{remote}/{main}")
        if isinstance(head, ReadError):
            return f"{head.command}: {head}"
        r1_sha = head.sha.lower()

    anchor = adapter.read_canonical_anchor()
    if isinstance(anchor, ReadError):
        return f"{anchor.command}: {anchor}"

    r3_sha: str | None = None
    r3_cmd: str | None = None
    if regime in {"muse+git-mirror", "muse-only"}:
        muse_main = config.vcs.muse.main_branch
        if not muse_main:
            return "muse.main_branch not configured"
        r3_cmd = f"muse rev-parse {muse_main}"
        head = adapter.read_head(f"muse:{muse_main}")
        if isinstance(head, ReadError):
            return f"{head.command}: {head}"
        r3_sha = head.sha.lower()
    elif regime == "git-only":
        r3_sha = r1_sha
        r3_cmd = r1_cmd

    return VerifiedReads(
        regime=regime,
        r1_github_main_sha=r1_sha,
        r1_command=r1_cmd,
        r2_anchor_sha=anchor.anchor_sha.lower(),
        r2_source=anchor.source,
        r3_canonical_main_sha=r3_sha,
        r3_command=r3_cmd,
        r4_merged_prs=(),
        r5_branch=status.branch.strip(),
        r5_dirty=status.dirty,
        r5_regime=status.regime,
    )


def _load_default_lane_docs(config: OverseerConfig, repo_root: Path) -> tuple[str, str]:
    lane = config.docs.default_lane if config.docs.lanes is not None else None
    lane_docs = resolve_lane_docs(config, lane)
    handover_path = lane_living_doc_abs(repo_root, config, lane_docs, lane_docs.handover)
    roadmap_path = lane_living_doc_abs(repo_root, config, lane_docs, lane_docs.roadmap)
    handover = handover_path.read_text(encoding="utf-8") if handover_path.is_file() else ""
    roadmap = roadmap_path.read_text(encoding="utf-8") if roadmap_path.is_file() else ""
    return handover, roadmap

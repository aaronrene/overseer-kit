"""Typed results for the Governance Hygiene Agent (§9A-5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DriftState = Literal["aligned", "drifted", "unreadable"]


@dataclass(frozen=True)
class MergedPullRequest:
    """One row from ``gh pr list --state merged`` (R4)."""

    number: int
    title: str
    merge_commit_sha: str
    merged_at: str


@dataclass(frozen=True)
class VerifiedReads:
    """Snapshot of R1–R5 verified reads."""

    regime: str
    r1_github_main_sha: str | None
    r1_command: str | None
    r2_anchor_sha: str
    r2_source: str
    r3_canonical_main_sha: str | None
    r3_command: str | None
    r4_merged_prs: tuple[MergedPullRequest, ...]
    r5_branch: str
    r5_dirty: bool
    r5_regime: str


@dataclass(frozen=True)
class DriftReport:
    """Typed drift detection result (D1–D3)."""

    d1_handover_vs_git: DriftState
    d2_anchor_vs_canonical: DriftState
    d3_queue_vs_merged: DriftState
    details: dict[str, str] = field(default_factory=dict)

    @property
    def any_drifted(self) -> bool:
        return any(
            state == "drifted"
            for state in (self.d1_handover_vs_git, self.d2_anchor_vs_canonical, self.d3_queue_vs_merged)
        )

    @property
    def any_unreadable(self) -> bool:
        return any(
            state == "unreadable"
            for state in (self.d1_handover_vs_git, self.d2_anchor_vs_canonical, self.d3_queue_vs_merged)
        )

    @property
    def fully_aligned(self) -> bool:
        return not self.any_drifted and not self.any_unreadable


@dataclass(frozen=True)
class QueueRow:
    """One parsed roadmap build-queue row (D3 claim)."""

    phase_label: str
    model: str
    status: str
    deliverable: str
    raw_line: str


@dataclass(frozen=True)
class PatchPlan:
    """Planned doc patches before apply."""

    handover_text: str
    roadmap_text: str
    patched_sections: tuple[str, ...]
    realign_planned: bool
    realign_reason: str | None
    feature_branch: str
    commit_message: str
    pr_url: str | None


@dataclass(frozen=True)
class GovernanceSyncResult:
    """Outcome of a governance-sync run."""

    exit_code: int
    dry_run: bool
    reads: VerifiedReads | None
    drift: DriftReport | None
    plan: PatchPlan | None
    committed: bool
    commit_sha: str | None
    messages: tuple[str, ...]
    error_command: str | None = None

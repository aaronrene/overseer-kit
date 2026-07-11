"""Unit tests for governance drift detection (§8 unit tier)."""

from __future__ import annotations

from tools.governance_hygiene.drift import detect_drift
from tools.governance_hygiene.types import MergedPullRequest, VerifiedReads


def _reads(github_main: str = "cafebabe") -> VerifiedReads:
    return VerifiedReads(
        regime="git-only",
        r1_github_main_sha=github_main,
        r1_command="git rev-parse origin/main",
        r2_anchor_sha=github_main,
        r2_source="origin/main",
        r3_canonical_main_sha=github_main,
        r3_command="git rev-parse origin/main",
        r4_merged_prs=(),
        r5_branch="main",
        r5_dirty=False,
        r5_regime="git-only",
    )


def test_detect_drift_d1_drifted_d2_d3_aligned() -> None:
    handover = "| **main HEAD** | `deadbeef` |"
    roadmap = "| **9A-5 Governance Hygiene Agent** | Auto | **TODO** | x |"
    drift = detect_drift(_reads("cafebabe"), handover, roadmap)
    assert drift.d1_handover_vs_git == "drifted"
    assert drift.d2_anchor_vs_canonical == "aligned"
    assert drift.d3_queue_vs_merged == "aligned"


def test_detect_drift_fully_aligned() -> None:
    handover = "| **main HEAD** | `cafebabe` |"
    roadmap = "| **9A-5 Governance Hygiene Agent** | Auto | **TODO** | x |"
    drift = detect_drift(_reads(), handover, roadmap)
    assert drift.fully_aligned is True

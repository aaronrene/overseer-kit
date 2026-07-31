"""Unit tests for governance drift detection (§8 unit tier)."""

from __future__ import annotations

from dataclasses import replace

from tools.governance_hygiene.drift import detect_drift
from tools.governance_hygiene.parse import pr_matches_row
from tools.governance_hygiene.types import MergedPullRequest, QueueRow, VerifiedReads


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


def _row(label: str, status: str = "**NEXT**") -> QueueRow:
    return QueueRow(phase_label=label, model="Thinking", status=status, deliverable="x", raw_line="|")


_GSW_LAND_B_TITLE = "Mirror: mirror: GSW land-b docs sync + muse code add staging fix"


def test_pr_match_rejects_generic_fragment_overlap() -> None:
    """Live GSW land-b regression: a mirror PR title sharing only boilerplate
    words (land / sync / main / post) must never stamp an unrelated open row."""
    assert pr_matches_row(_GSW_LAND_B_TITLE, _row("**PLS-a Post-land main sync freeze**")) is False
    assert pr_matches_row(_GSW_LAND_B_TITLE, _row("**PLS-b Post-land main sync build**")) is False


def test_pr_match_accepts_slice_identifying_token() -> None:
    assert pr_matches_row(_GSW_LAND_B_TITLE, _row("**GSW-FIX → main**")) is True
    assert pr_matches_row(
        "Mirror: PMHF post-merge handover freshness land closeout",
        _row("**PMHF → main**"),
    ) is True


def test_pr_match_requires_word_boundary() -> None:
    """Slice IDs must match as whole words — `PLS` inside `pulse` is no match."""
    assert pr_matches_row("chore: pulse metrics cleanup", _row("**PLS-a Post-land main sync freeze**")) is False


def test_pr_match_full_label_substring_still_matches() -> None:
    assert pr_matches_row(
        "feat: K10 Honesty module ledger gates",
        _row("**K10 Honesty module**"),
    ) is True


def test_detect_drift_d3_ignores_generic_overlap_with_open_row() -> None:
    """D3 stays aligned when the only 'match' against an open row is boilerplate."""
    handover = "| **main HEAD** | `cafebabe` |"
    roadmap = "| **PLS-a Post-land main sync freeze** | Thinking | **NEXT** | x |"
    reads = _reads()
    reads = replace(reads, r4_merged_prs=(
        MergedPullRequest(number=54, title=_GSW_LAND_B_TITLE, merge_commit_sha="e895a35" + "0" * 33, merged_at="2026-07-31T16:00:00Z"),
    ))
    drift = detect_drift(reads, handover, roadmap)
    assert drift.d3_queue_vs_merged == "aligned"

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
_GSW_CLOSEOUT_TITLE = (
    "Mirror: mirror: GSW closeout — queue PLS post-land sync + pr_matches_row slice-token fix"
)


def test_pr_match_rejects_generic_fragment_overlap() -> None:
    """Live GSW land-b regression: a mirror PR title sharing only boilerplate
    words (land / sync / main / post) must never stamp an unrelated open row."""
    assert pr_matches_row(_GSW_LAND_B_TITLE, _row("**PLS-a Post-land main sync freeze**")) is False
    assert pr_matches_row(_GSW_LAND_B_TITLE, _row("**PLS-b Post-land main sync build**")) is False


def test_pr_match_rejects_bare_prefix_when_compound_id_exists() -> None:
    """Live PR #55 closeout: title 'queue PLS …' must not stamp open PLS-a/PLS-b.
    Compound slice IDs (PLS-a) are required; bare PLS is not enough."""
    assert pr_matches_row(_GSW_CLOSEOUT_TITLE, _row("**PLS-a Post-land main sync freeze**")) is False
    assert pr_matches_row(_GSW_CLOSEOUT_TITLE, _row("**PLS-b Post-land main sync build**")) is False
    assert pr_matches_row(
        "feat(PLS-a): freeze post-land main sync",
        _row("**PLS-a Post-land main sync freeze**"),
    ) is True


def test_pr_match_accepts_compound_slice_id() -> None:
    assert pr_matches_row(
        "mirror: GSW-FIX governance-sync write-path",
        _row("**GSW-FIX → main**"),
    ) is True
    # Bare GSW without the compound GSW-FIX is not enough when the label has one.
    assert pr_matches_row(_GSW_LAND_B_TITLE, _row("**GSW-FIX → main**")) is False


def test_pr_match_accepts_non_compound_slice_token() -> None:
    """Labels without hyphenated IDs still match on a distinctive token (PMHF)."""
    assert pr_matches_row(
        "Mirror: PMHF post-merge handover freshness land closeout",
        _row("**PMHF → main**"),
    ) is True


def test_pr_match_rejects_visibility_checklist_overlap() -> None:
    """Live ONS land-b regression: Contributor PR #63 title sharing only
    English product words (visibility / checklist) must never stamp the
    open Tier-3 row ``Public repository visibility flip`` DONE."""
    contributor_title = (
        "Mirror: mirror: Contributor prep — CONTRIBUTING, laundry purge, "
        "visibility checklist"
    )
    assert (
        pr_matches_row(
            contributor_title,
            _row("**Public repository visibility flip**"),
        )
        is False
    )
    # Full-label substring still matches when the PR is truly about the flip.
    assert (
        pr_matches_row(
            "Mirror: Public repository visibility flip — Settings private→public",
            _row("**Public repository visibility flip**"),
        )
        is True
    )


def test_pr_match_requires_word_boundary() -> None:
    """Slice IDs must match as whole words — `PLS` inside `pulse` is no match."""
    assert pr_matches_row("chore: pulse metrics cleanup", _row("**PLS-a Post-land main sync freeze**")) is False


def test_pr_match_full_label_substring_still_matches() -> None:
    assert pr_matches_row(
        "feat: K10 Honesty module ledger gates",
        _row("**K10 Honesty module**"),
    ) is True


def test_detect_drift_d3_ignores_mention_of_queued_slice() -> None:
    """D3 stays aligned when a merged PR only *mentions* a still-open slice."""
    handover = "| **main HEAD** | `cafebabe` |"
    roadmap = (
        "| **PLS-a Post-land main sync freeze** | Thinking | **NEXT** | x |\n"
        "| **PLS-b Post-land main sync build** | Auto | **QUEUED** | x |"
    )
    reads = replace(
        _reads(),
        r4_merged_prs=(
            MergedPullRequest(
                number=55,
                title=_GSW_CLOSEOUT_TITLE,
                merge_commit_sha="4650171" + "0" * 33,
                merged_at="2026-07-31T16:45:00Z",
            ),
        ),
    )
    drift = detect_drift(reads, handover, roadmap)
    assert drift.d3_queue_vs_merged == "aligned"

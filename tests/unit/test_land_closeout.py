"""Unit tests for land-closeout resolution (§PMHF.10 unit).

Covers the frozen ``check_land_closeout`` resolution table, the §PMHF.4.2
vocabulary fallback (including the frozen false-positive exclusions), the
``land_phase_conflicts_queue_done`` token-intersection check, and the
``ok`` vs ``land_complete`` distinction.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from adapters.runner import CommandResult, RecordingRunner
from adapters.types import AnchorResult, HeadResult, StatusResult
from tests.support import (
    LAND_A_MARKER,
    LAND_B_MARKER,
    land_a_fence_body,
    land_b_fence_body,
    land_handover_text,
    land_roadmap_text,
    load_fixture_config,
    seed_land_repo,
    write_config,
)
from tools.governance_hygiene.next_regen import (
    LAND_PHASE_A,
    LAND_PHASE_B,
    LAND_PHASE_UNREADABLE,
    extract_land_id,
    land_queue_conflict,
    resolve_land_phase,
    set_marker_land_phase,
    strip_land_parenthetical,
)
from tools.land_closeout import check_land_closeout, land_complete


def _adapter(*, tip: str = "cafebabe") -> MagicMock:
    adapter = MagicMock()
    adapter.status.return_value = StatusResult(
        regime="git-only", dirty=False, branch="main", muse_dirty=None, git_dirty=False
    )
    adapter.read_head.return_value = HeadResult(sha=tip, kind="git")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha=tip, source="origin/main"
    )
    return adapter


def _check(tmp_path: Path, **kwargs):
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    adapter = kwargs.pop("adapter", None) or _adapter(tip=kwargs.pop("tip", "cafebabe"))
    return check_land_closeout(config, tmp_path, adapter=adapter, **kwargs)


# --- resolution table (§PMHF.5.2) ---


def test_not_applicable_without_lock(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    report = _check(tmp_path)
    assert report.state == "not_applicable"
    assert report.ok
    assert land_complete(report)


def test_not_applicable_when_no_land_posture(tmp_path: Path) -> None:
    seed_land_repo(
        tmp_path,
        handover_text=land_handover_text(
            marker=None,
            heading="PMHF-b Build",
            fence_body="Model: Auto\nID: PMHF-b\n\nBuild the thing.\n",
        ),
    )
    report = _check(tmp_path)
    assert report.state == "not_applicable"
    assert report.land_phase is None
    assert report.ok


def test_land_a_in_progress_when_aligned(tmp_path: Path) -> None:
    seed_land_repo(tmp_path)
    report = _check(tmp_path)
    assert report.state == "land_a_in_progress"
    assert report.land_phase == "land-a"
    assert report.ok  # status floor must not fail while waiting for merge
    assert not land_complete(report)  # …but land is NOT complete (§PMHF.3.3)


def test_post_merge_incomplete_when_d1_drifted(tmp_path: Path) -> None:
    seed_land_repo(tmp_path, claim="deadbeef")
    report = _check(tmp_path, tip="cafebabe")
    assert report.state == "post_merge_incomplete"
    assert not report.ok
    assert report.d1 == "drifted"
    assert (report.remediation or "").startswith(
        "land-b required: ok governance-sync --dry-run then apply; "
        "paste land-b; do not re-paste land-a"
    )


def test_post_merge_incomplete_when_stale_marker(tmp_path: Path) -> None:
    seed_land_repo(tmp_path, marker_tip=None)  # D1 aligned; sync marker absent
    report = _check(tmp_path)
    assert report.state == "post_merge_incomplete"
    assert not report.ok


def test_land_b_in_progress_when_drifted(tmp_path: Path) -> None:
    seed_land_repo(
        tmp_path,
        claim="deadbeef",
        handover_text=land_handover_text(
            claim="deadbeef",
            marker=LAND_B_MARKER,
            heading="PMHF land-b (post-merge sync)",
            fence_body=land_b_fence_body(),
        ),
    )
    report = _check(tmp_path, tip="cafebabe")
    assert report.state == "land_b_in_progress"
    assert not report.ok
    assert "governance-sync" in (report.remediation or "")


def test_complete_when_land_b_and_fresh(tmp_path: Path) -> None:
    seed_land_repo(
        tmp_path,
        handover_text=land_handover_text(
            marker=LAND_B_MARKER,
            heading="PMHF land-b (post-merge sync)",
            fence_body=land_b_fence_body(),
        ),
    )
    report = _check(tmp_path)
    assert report.state == "complete"
    assert report.ok
    assert land_complete(report)


def test_unreadable_on_unknown_land_phase_value(tmp_path: Path) -> None:
    bad_marker = LAND_A_MARKER.replace("land-phase=land-a", "land-phase=weird")
    seed_land_repo(tmp_path, handover_text=land_handover_text(marker=bad_marker))
    report = _check(tmp_path)
    assert report.state == "unreadable"
    assert not report.ok
    assert not land_complete(report)


def test_unreadable_freshness_not_masked_as_post_merge_incomplete(tmp_path: Path) -> None:
    seed_land_repo(tmp_path)
    adapter = MagicMock()
    from adapters.errors import ReadError

    adapter.status.return_value = ReadError("git status", "boom")
    report = _check(tmp_path, adapter=adapter)
    assert report.state == "unreadable"  # R2-M2: never masked


# --- §PMHF.4 marker + vocabulary fallback ---


def test_vocabulary_fallback_wait_for_merge_is_land_a(tmp_path: Path) -> None:
    text = land_handover_text(
        claim="deadbeef",
        marker=None,
        fence_body=(
            "Model: Operator + Auto\nID: PMHF → main\n\n"
            "Open PR #206 and wait for merge before continuing.\n"
        ),
    )
    assert resolve_land_phase(text) == LAND_PHASE_A
    seed_land_repo(tmp_path, claim="deadbeef", handover_text=text)
    report = _check(tmp_path, tip="cafebabe")
    assert report.state == "post_merge_incomplete"


def test_bare_open_pr_alone_does_not_trigger_land_a() -> None:
    text = land_handover_text(
        marker=None,
        heading="PMHF-b Build",
        fence_body=(
            "Model: Auto\nID: PMHF-b\n\n"
            "Deliver:\n1. Build feature\n2. open PR from the feature branch\n"
            "3. open/update PR as needed (Tier 3 applies to main)\n"
        ),
    )
    assert resolve_land_phase(text) is None


def test_conflicting_vocabulary_is_unreadable() -> None:
    text = land_handover_text(
        marker=None,
        fence_body=(
            "Model: Auto\nID: PMHF\n\n"
            "wait for merge, then run land-b (post-merge sync)\n"
        ),
    )
    assert resolve_land_phase(text) == LAND_PHASE_UNREADABLE


def test_marker_attribute_beats_vocabulary(tmp_path: Path) -> None:
    # Marker says land-b; fence still carries land-a vocabulary.
    text = land_handover_text(
        marker=LAND_B_MARKER,
        fence_body="Model: Auto\nID: PMHF land-b (post-merge sync)\n\nwait for merge\n",
    )
    assert resolve_land_phase(text) == LAND_PHASE_B
    seed_land_repo(tmp_path, handover_text=text)
    report = _check(tmp_path)
    assert report.state == "complete"


def test_set_marker_land_phase_roundtrip() -> None:
    text = land_handover_text()
    cleared = set_marker_land_phase(text, None)
    assert "land-phase=" not in cleared
    stamped = set_marker_land_phase(cleared, "land-b")
    assert resolve_land_phase(stamped) == LAND_PHASE_B


# --- §PMHF.3.3 queue conflict ---


def test_land_id_extraction_strips_parenthetical() -> None:
    text = land_handover_text()
    land_id = extract_land_id(text)
    assert land_id == "PMHF → main (land-a)"
    assert strip_land_parenthetical(land_id) == "PMHF → main"


def test_land_phase_conflicts_queue_done_token(tmp_path: Path) -> None:
    seed_land_repo(
        tmp_path,
        roadmap_text=land_roadmap_text(
            "| **PMHF → main** | Operator + Auto | **DONE** | Land PMHF |",
        ),
    )
    report = _check(tmp_path)
    assert report.state == "unreadable"
    assert "land_phase_conflicts_queue_done" in report.message
    assert not report.ok


def test_historical_other_slice_land_row_does_not_conflict(tmp_path: Path) -> None:
    seed_land_repo(
        tmp_path,
        roadmap_text=land_roadmap_text(
            "| **GS-PASTE → main** | Operator + Auto | **DONE** | Landed earlier |",
            "| **GFG → main** | Operator + Auto | **MERGED** | Landed earlier |",
            "| **PMHF → main** | Operator + Auto | **TODO** | Land PMHF |",
        ),
    )
    report = _check(tmp_path)
    assert report.state == "land_a_in_progress"


def test_queue_conflict_requires_land_shaped_row() -> None:
    # A DONE build row sharing the slice token is not a land row — no conflict.
    roadmap = land_roadmap_text(
        "| **PMHF-b Build** | Auto | **DONE** | build |",
        "| **PMHF → main** | Operator + Auto | **TODO** | Land PMHF |",
    )
    assert not land_queue_conflict(roadmap, "PMHF → main (land-a)")
    assert land_queue_conflict(
        land_roadmap_text("| **PMHF → main** | Operator + Auto | **DONE** | landed |"),
        "PMHF → main (land-a)",
    )


# --- §PMHF.5.3 optional merged-PR enrichment ---


def _pr_handover(claim: str = "cafebabe") -> str:
    return land_handover_text(
        claim=claim,
        fence_body=land_a_fence_body(paste_extra="PR #206 open — waiting for merge.\n"),
    )


def test_probe_merged_pr_catches_hand_edited_alignment(tmp_path: Path) -> None:
    seed_land_repo(tmp_path, handover_text=_pr_handover())
    runner = RecordingRunner(
        responses={
            "gh pr view 206 --json state,mergedAt": CommandResult(
                stdout='{"state": "MERGED", "mergedAt": "2026-07-30T12:00:00Z"}',
                stderr="",
                exit_code=0,
            )
        },
        calls=[],
    )
    report = _check(tmp_path, runner=runner, probe_merged_pr=True)
    assert report.optional_pr_merged is True
    assert report.state == "post_merge_incomplete"


def test_probe_merged_pr_gh_failure_never_fails_open(tmp_path: Path) -> None:
    seed_land_repo(tmp_path, handover_text=_pr_handover())
    runner = RecordingRunner(responses={}, calls=[])  # gh unavailable
    report = _check(tmp_path, runner=runner, probe_merged_pr=True)
    assert report.optional_pr_merged is None
    assert report.state == "land_a_in_progress"  # not complete, not fabricated


def test_no_gh_when_probe_disabled(tmp_path: Path) -> None:
    seed_land_repo(tmp_path, handover_text=_pr_handover())
    runner = RecordingRunner(responses={}, calls=[])
    report = _check(tmp_path, runner=runner, probe_merged_pr=False)
    assert report.optional_pr_merged is None
    assert not any("gh" in call[0] for call in runner.calls)


# --- ok vs land_complete (§PMHF.3.3) ---


def test_ok_vs_land_complete_distinction(tmp_path: Path) -> None:
    seed_land_repo(tmp_path)
    report = _check(tmp_path)
    assert report.state == "land_a_in_progress"
    assert report.ok is True
    assert land_complete(report) is False

"""Stress: land-closeout on large handover/roadmap stays bounded (§PMHF.10 stress)."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock

from adapters.runner import RecordingRunner
from adapters.types import AnchorResult, HeadResult, StatusResult
from tests.support import land_handover_text, load_fixture_config, seed_land_repo
from tools.land_closeout import check_land_closeout


def _adapter(tip: str = "cafebabe") -> MagicMock:
    adapter = MagicMock()
    adapter.status.return_value = StatusResult(
        regime="git-only", dirty=False, branch="main", muse_dirty=None, git_dirty=False
    )
    adapter.read_head.return_value = HeadResult(sha=tip, kind="git")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha=tip, source="origin/main"
    )
    return adapter


def _large_roadmap(rows: int = 250) -> str:
    lines = [
        "# Roadmap — stress fixture",
        "",
        "## Build queue",
        "",
        "| Phase | Model | Status | Deliverable |",
        "| --- | --- | --- | --- |",
    ]
    for index in range(rows):
        # Historical DONE land rows for other slices must not conflict.
        lines.append(
            f"| **SLICE{index} → main** | Operator + Auto | **DONE** | landed slice {index} |"
        )
    lines.append("| **PMHF → main** | Operator + Auto | **TODO** | Land PMHF |")
    lines.extend(["", "## Definition of Done", "", "- Tests green"])
    return "\n".join(lines) + "\n"


def test_large_queue_and_handover_bounded_and_no_gh(tmp_path: Path) -> None:
    padding = "\n".join(f"- historical change log line {i}" for i in range(2000))
    handover = land_handover_text("cafebabe") + "\n" + padding + "\n"
    seed_land_repo(
        tmp_path,
        handover_text=handover,
        roadmap_text=_large_roadmap(),
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    runner = RecordingRunner(responses={}, calls=[])

    start = time.monotonic()
    report = check_land_closeout(
        config,
        tmp_path,
        adapter=_adapter(),
        runner=runner,
        probe_merged_pr=False,
    )
    elapsed = time.monotonic() - start

    assert elapsed < 2.0  # parse + freshness compose stays bounded
    assert report.state == "land_a_in_progress"  # 250 other-slice DONE rows: no conflict
    assert not any(call[0].startswith("gh") for call in runner.calls)


def test_large_queue_conflict_still_detected(tmp_path: Path) -> None:
    roadmap = _large_roadmap().replace(
        "| **PMHF → main** | Operator + Auto | **TODO** | Land PMHF |",
        "| **PMHF → main** | Operator + Auto | **DONE** | Land PMHF |",
    )
    seed_land_repo(tmp_path, roadmap_text=roadmap)
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_land_closeout(config, tmp_path, adapter=_adapter())
    assert report.state == "unreadable"
    assert "land_phase_conflicts_queue_done" in report.message

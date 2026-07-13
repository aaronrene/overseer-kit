"""Performance tests for Track P / P-cost (§PC.9)."""

from __future__ import annotations

import time
from pathlib import Path

from adapters.config import load_config
from cli.kit_root import kit_root
from tests.fixtures.cost_awareness import seed_cost_e2e_repo
from tests.support import git_status_runner, run_cli
from tools.cost_awareness.surface import build_cost_awareness_report


def test_route_annotation_bounded(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    start = time.perf_counter()
    code = run_cli(
        ["route", "--phase-tier", "auto", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    elapsed = time.perf_counter() - start
    assert code == 0
    assert elapsed < 2.0


def test_active_slice_surface_bounded(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    handover = (tmp_path / "docs" / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8")
    roadmap = (tmp_path / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    start = time.perf_counter()
    report = build_cost_awareness_report(
        config, tmp_path, kit_root=kit_root(), handover_text=handover, roadmap_text=roadmap
    )
    elapsed = time.perf_counter() - start
    assert report.enabled is True
    assert elapsed < 2.0

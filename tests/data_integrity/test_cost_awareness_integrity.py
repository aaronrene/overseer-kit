"""Data-integrity tests for Track P / P-cost (§PC.9)."""

from __future__ import annotations

import json
from pathlib import Path

from adapters.config import load_config
from cli.kit_root import kit_root
from tests.fixtures.cost_awareness import seed_cost_awareness_repo, seed_cost_e2e_repo
from tests.support import git_status_runner, run_cli
from tools.cost_awareness.derive import derive_cost_view
from tools.cost_awareness.surface import build_cost_awareness_report


def test_surface_idempotent_same_inputs(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    handover = (tmp_path / "docs" / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8")
    roadmap = (tmp_path / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    first = build_cost_awareness_report(
        config, tmp_path, kit_root=kit_root(), handover_text=handover, roadmap_text=roadmap
    )
    second = build_cost_awareness_report(
        config, tmp_path, kit_root=kit_root(), handover_text=handover, roadmap_text=roadmap
    )
    assert first == second


def test_paid_derivation_deterministic() -> None:
    bands = {"standard": "moderate", "fast": "low"}
    results = {derive_cost_view("standard", bands) for _ in range(20)}
    assert results == {("moderate", True)}


def test_enabling_cost_awareness_does_not_mutate_files(tmp_path: Path) -> None:
    seed_cost_awareness_repo(tmp_path, enabled=True)
    lock_path = tmp_path / ".overseer" / "version.lock"
    lock_path.write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:abc\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
    )
    before = lock_path.read_bytes()
    run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert lock_path.read_bytes() == before


def test_disabled_cost_awareness_status_unchanged(tmp_path: Path, capsys) -> None:
    seed_cost_awareness_repo(tmp_path, enabled=False)
    lock_path = tmp_path / ".overseer" / "version.lock"
    lock_path.write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:abc\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
    )
    run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    payload = json.loads(capsys.readouterr().out)
    assert "cost_awareness" not in payload

"""Stress: large preserved living docs under migrate (§K6.10)."""

from __future__ import annotations

from pathlib import Path

from tests.support import PILOT, git_status_runner, muse_mirror_status_runner, run_cli, seed_pilot_tree


def test_large_preserved_docs_migrate_status_bounded(tmp_path: Path) -> None:
    big = "# large\n" + ("x" * 200_000) + "\n"
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text=big,
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text=big,
    )
    runner = muse_mirror_status_runner(tmp_path)
    assert (
        run_cli(
            [
                "init",
                "--migrate",
                "--from-config",
                str(PILOT / "config-scooling.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    assert run_cli(["status", "--check-footprint"], cwd=tmp_path, runner=runner) == 0
    assert (
        tmp_path / "docs/OVERSEER-HANDOVER.md"
    ).read_text(encoding="utf-8") == big

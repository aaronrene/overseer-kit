"""Stress — many differing shared assets preserved in one migrate (§PSA.8)."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import ORIGIN_PRESERVED, read_version_lock
from tests.support import PILOT, muse_mirror_status_runner, run_cli, seed_pilot_tree


def test_many_differing_shared_assets_preserved(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    policy = tmp_path / ".overseer" / "policy"
    policy.mkdir(parents=True, exist_ok=True)
    shared_paths = [
        ".overseer/policy/tiers.yaml",
        ".overseer/policy/model-labels.yaml",
        ".overseer/policy/test-tiers.yaml",
    ]
    for rel in shared_paths:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# consumer {rel}\n" + ("y" * 50_000) + "\n", encoding="utf-8")

    code = run_cli(
        [
            "init",
            "--migrate",
            "--force",
            "--preserve-shared-assets",
            "--from-config",
            str(PILOT / "config-scooling.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    by_path = {e.path: e for e in lock.footprint}
    for rel in shared_paths:
        assert (tmp_path / rel).read_text(encoding="utf-8").startswith(f"# consumer {rel}")
        assert by_path[rel].origin == ORIGIN_PRESERVED

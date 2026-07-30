"""Performance — preserve-shared-assets migrate bound (§PSA.8)."""

from __future__ import annotations

import time
from pathlib import Path

from tests.support import PILOT, muse_mirror_status_runner, run_cli, seed_pilot_tree

MAX_PRESERVE_MIGRATE_SECONDS = 5.0


def test_preserve_shared_migrate_bounded(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    policy = tmp_path / ".overseer" / "policy"
    policy.mkdir(parents=True, exist_ok=True)
    (policy / "tiers.yaml").write_text("altered: true\n", encoding="utf-8")

    start = time.perf_counter()
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
    elapsed = time.perf_counter() - start
    assert code == 0
    assert elapsed < MAX_PRESERVE_MIGRATE_SECONDS

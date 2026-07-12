"""Performance: pilot status + governance-sync dry-run bounded (§K6.10)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from tests.support import PILOT, muse_mirror_status_runner, ok, run_cli, seed_pilot_tree


def test_pilot_status_and_dry_run_bounded(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n" + ("row\n" * 500),
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n" + ("row\n" * 500),
    )
    runner = muse_mirror_status_runner(tmp_path)
    root = str(tmp_path.resolve())
    runner.responses.update(
        {
            f"muse -C {root} rev-parse main": ok('{"commit_id": "' + "a" * 40 + '"}'),
            "git rev-parse origin/main": ok("b" * 40),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                json.dumps([])
            ),
        }
    )
    (tmp_path / ".muse").mkdir(exist_ok=True)
    (tmp_path / ".muse" / "git-bridge.toml").write_text(
        '[last_export]\ngit_sha = "' + ("c" * 40) + '"\n'
        '[last_import]\ngit_sha = "' + ("c" * 40) + '"\n',
        encoding="utf-8",
    )
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

    start = time.perf_counter()
    assert run_cli(["status", "--check-footprint"], cwd=tmp_path, runner=runner) == 0
    run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner)
    elapsed = time.perf_counter() - start
    assert elapsed < 5.0
    # Bounded VCS scans: status + dry-run must not unbounded-loop
    assert len(runner.calls) < 40

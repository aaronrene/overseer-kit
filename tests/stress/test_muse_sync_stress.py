"""Stress test: muse-sync gate stays O(1) regardless of how many files Muse reports (§KH2.8 stress tier)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from tests.support import FIXTURES, make_runner, ok, run_cli, seed_muse_substrate


def test_muse_sync_gate_bounded_with_large_muse_status_payload(tmp_path: Path) -> None:
    root = str(tmp_path.resolve())
    # Muse's own status --json is free to report thousands of changed files; the gate
    # only ever inspects the boolean `dirty` field, never the file list itself.
    huge_payload = json.dumps(
        {
            "dirty": True,
            "total_changes": 5000,
            "changes": [f"src/module_{i}.py" for i in range(5000)],
        }
    )
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok(huge_payload),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
        }
    )
    assert (
        run_cli(
            [
                "init",
                "--from-config",
                str(FIXTURES / "config-muse-git-mirror.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    seed_muse_substrate(tmp_path)

    start = time.perf_counter()
    code = run_cli(["status", "--exit-code"], cwd=tmp_path, runner=runner)
    elapsed = time.perf_counter() - start

    assert code == 2
    assert elapsed < 5.0

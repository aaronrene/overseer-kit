"""Performance tests for K7 status --check-footprint with bridge files (§K7.8 performance tier)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.footprint import MUSE_BRIDGE_WORKFLOW_DEST
from tests.support import FIXTURES, muse_mirror_status_runner, run_cli


def test_check_footprint_bounded_with_bridge_files(tmp_path: Path) -> None:
    runner = muse_mirror_status_runner(tmp_path)
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
    workflow = tmp_path / MUSE_BRIDGE_WORKFLOW_DEST
    workflow.write_text(workflow.read_text(encoding="utf-8") + ("\n# padding\n" * 2000), encoding="utf-8")

    start = time.perf_counter()
    code = run_cli(["status", "--check-footprint", "--exit-code"], cwd=tmp_path, runner=runner)
    elapsed = time.perf_counter() - start
    assert code == 6  # footprint integrity mismatch (--exit-code precedence)
    assert elapsed < 5.0

    # Restore kit bytes and confirm fast OK path
    run_cli(
        [
            "init",
            "--from-config",
            str(FIXTURES / "config-muse-git-mirror.yaml"),
            "--non-interactive",
            "--force",
        ],
        cwd=tmp_path,
        runner=runner,
    )
    start = time.perf_counter()
    assert run_cli(["status", "--check-footprint"], cwd=tmp_path, runner=runner) == 0
    elapsed = time.perf_counter() - start
    assert elapsed < 5.0

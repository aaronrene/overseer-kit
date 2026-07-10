"""Performance tests for bounded status execution."""

from __future__ import annotations

import time
from pathlib import Path

from tests.support import git_status_runner, run_cli


def test_status_completes_within_budget(tmp_path: Path) -> None:
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path)
    runner = git_status_runner()
    start = time.monotonic()
    code = run_cli(["status"], cwd=tmp_path, runner=runner)
    elapsed = time.monotonic() - start
    assert code == 0
    assert elapsed < 1.0
    status_calls = [c for c in runner.calls if "status" in c[0]]
    assert len(status_calls) <= 2

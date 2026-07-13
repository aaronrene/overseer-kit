"""Performance tests for Track Q / Q2b OK CLI entrypoint (§Q2A.10)."""

from __future__ import annotations

import time
from pathlib import Path

from tests.support import run_cli, run_shim, seed_git_repo, write_config


def test_ok_shim_status_json_within_existing_budget(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    write_config(tmp_path, "config-git-only.yaml")
    run_cli(["init", "--regime", "git-only", "--non-interactive", "--force"], cwd=tmp_path)

    start = time.monotonic()
    result = run_shim("ok", ["status", "--json"], cwd=tmp_path)
    elapsed = time.monotonic() - start
    assert result.exit_code == 0
    assert elapsed < 1.0

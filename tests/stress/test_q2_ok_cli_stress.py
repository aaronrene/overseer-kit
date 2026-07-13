"""Stress tests for Track Q / Q2b OK CLI entrypoint (§Q2A.10)."""

from __future__ import annotations

from pathlib import Path

from tests.support import OVERSEER_DEPRECATION_LINE, run_cli, run_shim, seed_git_repo, write_config


def test_overseer_shim_deprecation_is_one_line_per_process(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    write_config(tmp_path, "config-git-only.yaml")
    run_cli(["init", "--regime", "git-only", "--non-interactive", "--force"], cwd=tmp_path)

    for _ in range(20):
        result = run_shim("overseer", ["status"], cwd=tmp_path)
        assert result.exit_code == 0
        assert result.stderr == OVERSEER_DEPRECATION_LINE
        shim_temps = list(tmp_path.rglob("*.overseer.tmp"))
        assert shim_temps == []

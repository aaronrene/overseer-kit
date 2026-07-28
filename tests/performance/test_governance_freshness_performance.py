"""Performance: status GFG adds no gh invocation (§GFG.9 performance)."""

from __future__ import annotations

from pathlib import Path

from tests.support import FIXTURES, git_status_runner, run_cli, seed_governance_freshness


def test_status_exit_code_adds_no_gh_for_gfg(tmp_path: Path) -> None:
    runner = git_status_runner()
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    seed_governance_freshness(tmp_path)
    before = len(runner.calls)
    run_cli(["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True)
    new_cmds = [cmd for cmd, _ in runner.calls[before:]]
    assert not any(cmd.startswith("gh ") or " gh " in f" {cmd}" for cmd in new_cmds)
    assert any("git rev-parse origin/main" in cmd for cmd in new_cmds)

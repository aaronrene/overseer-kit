"""Security tests for Track Q / Q2b OK CLI entrypoint (§Q2A.10)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.support import KIT_ROOT, OVERSEER_DEPRECATION_LINE, run_cli, run_shim, seed_git_repo, write_config


def test_deprecation_line_has_no_absolute_paths_or_secrets() -> None:
    line = OVERSEER_DEPRECATION_LINE.strip()
    assert "/" not in line
    assert "Users" not in line
    assert "token" not in line.lower()
    assert line == "warning: 'overseer' is deprecated; use 'ok' (same commands)."


def test_overseer_json_stdout_is_single_object_deprecation_on_stderr(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    write_config(tmp_path, "config-git-only.yaml")
    run_cli(["init", "--regime", "git-only", "--non-interactive", "--force"], cwd=tmp_path)
    result = run_shim("overseer", ["status", "--json"], cwd=tmp_path)
    assert result.stderr == OVERSEER_DEPRECATION_LINE
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    assert "warning:" not in result.stdout


def test_shims_forward_args_without_shell_expansion(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    write_config(tmp_path, "config-git-only.yaml")
    run_cli(["init", "--regime", "git-only", "--non-interactive", "--force"], cwd=tmp_path)
    weird = run_shim("ok", ["status", "--json"], cwd=tmp_path)
    assert weird.exit_code == 0
    text = (KIT_ROOT / "cli" / "ok").read_text(encoding="utf-8")
    assert '"$@"' in text
    assert "eval" not in text

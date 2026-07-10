"""Unit tests for ``overseer status``."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from cli.context import CliContext
from cli.main import main
from cli.output import OutputContext
from tests.support import git_status_runner, run_cli


def test_uninitialized_repo(tmp_path: Path) -> None:
    code = run_cli(["status", "--json"], cwd=tmp_path)
    assert code == 0


def test_status_schema_includes_last_governance_sync_null(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
    )
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["status", "--json"],
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=git_status_runner(),
                output=OutputContext(json_mode=True),
            ),
        )
    assert code == 0
    payload = json.loads(out.getvalue())
    assert payload["last_governance_sync"] is None


def test_status_fail_closed_on_adapter_read_error(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
    )
    from tests.support import fail, make_runner

    code = run_cli(
        ["status"],
        cwd=tmp_path,
        runner=make_runner({"git rev-parse --abbrev-ref HEAD": fail("broken", 1)}),
    )
    assert code == 2


def test_exit_code_precedence(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
    )
    (tmp_path / ".overseer" / "config.yaml").write_text("bad: yaml\n", encoding="utf-8")
    code = run_cli(["status", "--exit-code", "--check-footprint"], cwd=tmp_path)
    assert code == 2

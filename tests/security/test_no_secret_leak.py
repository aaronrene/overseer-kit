"""Security tests — no secrets or absolute paths in output."""

from __future__ import annotations

import re
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from cli.context import CliContext
from cli.main import main
from cli.output import OutputContext
from tests.support import git_status_runner


ABS_PATH_RE = re.compile(r"/(?:Users|home|tmp|var)/")


def test_no_absolute_paths_in_status_json(tmp_path: Path) -> None:
    from tests.support import run_cli

    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path)
    out = StringIO()
    with patch("sys.stdout", out):
        main(
            ["status", "--json"],
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=git_status_runner(),
                output=OutputContext(json_mode=True),
            ),
        )
    text = out.getvalue()
    assert not ABS_PATH_RE.search(text)
    assert "token" not in text.lower()

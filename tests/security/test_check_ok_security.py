"""Security — Check-if-OK refuses path escape; no secrets in scaffold."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from cli.kit_root import kit_root
from tests.support import git_status_runner, run_cli, write_config
from tools.check_ok.scaffold import render_side_check_markdown, scaffold_side_check


def test_scaffold_rejects_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="path-escape"):
        scaffold_side_check(tmp_path, path="../../etc/passwd")


def test_cli_rejects_escape(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    code = run_cli(
        ["check-ok", "--path", "../../etc/passwd", "--scaffold-only"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4


def test_scaffold_body_has_no_secret_placeholders() -> None:
    body = render_side_check_markdown(
        topic="sec",
        phase_id="check-ok-sec",
        scope="security tier",
        output_path="docs/reviews/x.md",
        date_stamp="2026-07-17",
    )
    lowered = body.lower()
    assert "api_key" not in lowered
    assert "private_key" not in lowered
    assert "password" not in lowered

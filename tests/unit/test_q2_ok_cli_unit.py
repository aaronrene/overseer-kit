"""Unit tests for Track Q / Q2b OK CLI entrypoint (§Q2A.10)."""

from __future__ import annotations

import os
import stat
from io import StringIO

from cli.main import build_parser
from tests.support import KIT_ROOT, OVERSEER_DEPRECATION_LINE


def test_ok_shim_exists_executable_and_forwards_to_python_main() -> None:
    path = KIT_ROOT / "cli" / "ok"
    assert path.is_file()
    mode = path.stat().st_mode
    assert mode & stat.S_IXUSR
    text = path.read_text(encoding="utf-8")
    assert "python -m cli.main" in text
    assert OVERSEER_DEPRECATION_LINE.strip() not in text


def test_overseer_shim_exists_executable_with_exact_deprecation_line() -> None:
    path = KIT_ROOT / "cli" / "overseer"
    assert path.is_file()
    mode = path.stat().st_mode
    assert mode & stat.S_IXUSR
    text = path.read_text(encoding="utf-8")
    assert "python -m cli.main" in text
    assert f'echo "{OVERSEER_DEPRECATION_LINE.strip()}" >&2' in text


def test_argparse_prog_is_ok() -> None:
    parser = build_parser()
    assert parser.prog == "ok"


def test_help_usage_spells_ok() -> None:
    parser = build_parser()
    buffer = StringIO()
    parser.print_help(file=buffer)
    help_text = buffer.getvalue()
    assert "usage: ok" in help_text
    assert "usage: overseer" not in help_text

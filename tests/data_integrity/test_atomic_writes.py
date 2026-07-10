"""Data-integrity tests for atomic per-file writes."""

from __future__ import annotations

from pathlib import Path

from tests.support import run_cli


def test_no_half_written_file_on_failure(tmp_path: Path) -> None:
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path)
    target = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    original = target.read_bytes()

    from unittest.mock import patch

    with patch("cli.atomic.os.replace", side_effect=OSError("boom")):
        run_cli(
            ["init", "--regime", "git-only", "--non-interactive", "--force"],
            cwd=tmp_path,
        )

    assert not list(target.parent.glob(".*.overseer.tmp"))
    assert target.read_bytes() == original

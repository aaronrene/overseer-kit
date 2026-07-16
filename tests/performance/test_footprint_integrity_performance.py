"""Performance: the self-integrity gate adds no shell/adapter invocation (§KH3.8)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from cli.version_lock import ORIGIN_KIT, FootprintEntry, build_version_lock_from_entries
from tests.support import FIXTURES, git_status_runner, run_cli
from tools.footprint_integrity import check_footprint_integrity


def test_passing_precomputed_lock_avoids_a_second_disk_read(tmp_path: Path) -> None:
    """§KH3.5: `overseer status` reuses its already-loaded lock — no extra version.lock read."""
    lock = build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=[FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)],
        installed_at="2026-01-01T00:00:00Z",
    )
    (tmp_path / "a.mdc").write_text("x", encoding="utf-8")

    with patch("tools.footprint_integrity.check.read_version_lock") as mocked:
        report = check_footprint_integrity(tmp_path, lock=lock)
        mocked.assert_not_called()
    assert report.ok


def test_status_exit_code_adds_no_additional_shell_calls(tmp_path: Path) -> None:
    """`overseer status --exit-code` shell call count is identical whether the new gate is
    ``ok`` or ``missing`` — the gate performs pure filesystem stats, never shell commands."""
    runner = git_status_runner()
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )

    calls_before_reset = len(runner.calls)
    run_cli(["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True)
    ok_call_count = len(runner.calls) - calls_before_reset

    (tmp_path / ".cursor" / "rules" / "governance-sync.mdc").unlink()
    calls_before_missing = len(runner.calls)
    run_cli(["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True)
    missing_call_count = len(runner.calls) - calls_before_missing

    assert ok_call_count == missing_call_count

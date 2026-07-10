"""End-to-end install lifecycle test."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import read_version_lock
from tests.support import git_status_runner, run_cli


def test_full_install_cycle(tmp_path: Path) -> None:
    assert run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
        runner=git_status_runner(),
    ) == 0

    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.write_text(handover.read_text(encoding="utf-8") + "\n# local edit\n", encoding="utf-8")

    assert run_cli(
        ["status", "--check-footprint", "--exit-code"],
        cwd=tmp_path,
        runner=git_status_runner(),
    ) == 6

    assert run_cli(["sync", "-y"], cwd=tmp_path, runner=git_status_runner()) == 4

    assert run_cli(
        ["sync", "-y", "--force"],
        cwd=tmp_path,
        runner=git_status_runner(),
    ) == 0

    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert lock.kit_version == "0.1.0"

    assert run_cli(
        ["status", "--check-footprint"],
        cwd=tmp_path,
        runner=git_status_runner(),
    ) == 0

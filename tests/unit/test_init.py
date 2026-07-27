"""Unit tests for ``overseer init``."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.kit_root import kit_root
from cli.version_lock import read_version_lock
from tests.support import FIXTURES, run_cli


def test_init_creates_footprint_and_lock(tmp_path: Path) -> None:
    code = run_cli(
        ["init", "--regime", "git-only", "--repo-name", "demo", "--non-interactive"],
        cwd=tmp_path,
    )
    assert code == 0
    assert (tmp_path / ".overseer" / "config.yaml").is_file()
    assert (tmp_path / ".overseer" / "version.lock").is_file()
    assert (tmp_path / ".overseer" / "STANDING-DECISIONS.reference.md").is_file()
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert lock.kit_version == "0.1.0"


def test_init_missing_regime_non_interactive_fails_closed(tmp_path: Path) -> None:
    code = run_cli(["init", "--non-interactive"], cwd=tmp_path)
    assert code == 2


def test_init_refuse_without_force(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--repo-name", "demo", "--non-interactive"],
        cwd=tmp_path,
    )
    (tmp_path / "docs" / "DEMO-OVERSEER-HANDOVER.md").write_text("hand edit\n", encoding="utf-8")
    code = run_cli(
        ["init", "--regime", "git-only", "--repo-name", "demo", "--non-interactive"],
        cwd=tmp_path,
    )
    assert code == 4


def test_init_force_reinits(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--repo-name", "demo", "--non-interactive"],
        cwd=tmp_path,
    )
    (tmp_path / "docs" / "DEMO-OVERSEER-HANDOVER.md").write_text("hand edit\n", encoding="utf-8")
    code = run_cli(
        ["init", "--regime", "git-only", "--repo-name", "demo", "--non-interactive", "--force"],
        cwd=tmp_path,
    )
    assert code == 0
    assert "hand edit" not in (tmp_path / "docs" / "DEMO-OVERSEER-HANDOVER.md").read_text(
        encoding="utf-8"
    )


def test_init_noop_when_current(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
    )
    lock_path = tmp_path / ".overseer" / "version.lock"
    before = lock_path.read_text(encoding="utf-8")
    code = run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
    )
    assert code == 0
    assert lock_path.read_text(encoding="utf-8") == before


def test_init_from_config(tmp_path: Path) -> None:
    code = run_cli(
        [
            "init",
            "--from-config",
            str(FIXTURES / "config-git-only.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        kit=kit_root(),
    )
    assert code == 0


def test_init_dry_run_writes_nothing(tmp_path: Path) -> None:
    code = run_cli(
        ["init", "--regime", "git-only", "--non-interactive", "--dry-run"],
        cwd=tmp_path,
    )
    assert code == 0
    assert not (tmp_path / ".overseer" / "version.lock").exists()

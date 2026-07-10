"""Unit tests for ``overseer sync``."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import read_version_lock
from tests.support import run_cli


def _init(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
    )


def test_sync_noop_at_same_version(tmp_path: Path) -> None:
    _init(tmp_path)
    code = run_cli(["sync", "-y"], cwd=tmp_path)
    assert code == 0


def test_sync_refuse_consumer_modified(tmp_path: Path) -> None:
    _init(tmp_path)
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.write_text(handover.read_text(encoding="utf-8") + "\n# edited\n", encoding="utf-8")
    code = run_cli(["sync", "-y"], cwd=tmp_path)
    assert code == 4


def test_sync_force_applies(tmp_path: Path) -> None:
    _init(tmp_path)
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.write_text("consumer edit\n", encoding="utf-8")
    code = run_cli(["sync", "-y", "--force"], cwd=tmp_path)
    assert code == 0
    assert "consumer edit" not in handover.read_text(encoding="utf-8")


def test_sync_dry_run_writes_nothing(tmp_path: Path) -> None:
    _init(tmp_path)
    lock_before = read_version_lock(tmp_path / ".overseer" / "version.lock").synced_at
    code = run_cli(["sync", "--dry-run", "-y"], cwd=tmp_path)
    assert code == 0
    lock_after = read_version_lock(tmp_path / ".overseer" / "version.lock").synced_at
    assert lock_before == lock_after


def test_sync_missing_config_fails_closed(tmp_path: Path) -> None:
    code = run_cli(["sync", "-y"], cwd=tmp_path)
    assert code == 2

"""Unit tests for version.lock reader/writer."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.version_lock import (
    LockError,
    build_version_lock,
    read_version_lock,
    write_version_lock,
)


def test_round_trip(tmp_path: Path) -> None:
    lock = build_version_lock(
        kit_version="0.1.0",
        config_version=1,
        footprint=[("docs/A.md", "templates/A.template.md", b"hello\n")],
    )
    path = tmp_path / "version.lock"
    write_version_lock(path, lock)
    loaded = read_version_lock(path)
    assert loaded.kit_version == "0.1.0"
    assert len(loaded.footprint) == 1
    assert loaded.footprint[0].path == "docs/A.md"


def test_unknown_lock_version_raises(tmp_path: Path) -> None:
    path = tmp_path / "version.lock"
    path.write_text(
        "lock_version: 99\nkit_version: 0.1.0\nconfig_version: 1\n"
        'installed_at: "2026-01-01T00:00:00Z"\n'
        'synced_at: "2026-01-01T00:00:00Z"\n'
        'footprint_digest: "sha256:00"\nfootprint: []\n',
        encoding="utf-8",
    )
    with pytest.raises(LockError, match="unsupported lock_version"):
        read_version_lock(path)


def test_missing_keys_raises(tmp_path: Path) -> None:
    path = tmp_path / "version.lock"
    path.write_text("lock_version: 1\n", encoding="utf-8")
    with pytest.raises(LockError, match="missing required key"):
        read_version_lock(path)

"""Unit tests for the footprint self-integrity hard gate (§KH3.4)."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from cli.version_lock import (
    ORIGIN_KIT,
    ORIGIN_PRESERVED,
    FootprintEntry,
    build_version_lock_from_entries,
)
from tools.footprint_integrity import FootprintIntegrityReport, check_footprint_integrity


def _lock(entries: list[FootprintEntry]):
    return build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=entries,
        installed_at="2026-01-01T00:00:00Z",
    )


def test_no_lock_file_is_not_applicable(tmp_path: Path) -> None:
    """A repo with no version.lock at all has nothing declared yet — vacuously fine."""
    report = check_footprint_integrity(tmp_path)
    assert report.ok
    assert report.state == "not_applicable"
    assert report.missing == ()


def test_corrupt_lock_is_unreadable(tmp_path: Path) -> None:
    """A version.lock that exists but cannot be parsed fails closed, not silently ok."""
    overseer = tmp_path / ".overseer"
    overseer.mkdir(parents=True)
    (overseer / "version.lock").write_text("not: [valid, yaml, :::", encoding="utf-8")
    report = check_footprint_integrity(tmp_path)
    assert not report.ok
    assert report.state == "unreadable"
    assert report.remediation == "ok init"


def test_all_declared_present_is_ok(tmp_path: Path) -> None:
    (tmp_path / "a.mdc").write_text("x", encoding="utf-8")
    lock = _lock(
        [FootprintEntry(path="a.mdc", source="cursor/rules/a.mdc", sha256="0" * 64, origin=ORIGIN_KIT)]
    )
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.ok
    assert report.state == "ok"
    assert report.missing == ()


def test_declared_but_absent_is_missing(tmp_path: Path) -> None:
    """The exact frozen trigger: declared in version.lock, absent from disk."""
    lock = _lock(
        [FootprintEntry(path="a.mdc", source="cursor/rules/a.mdc", sha256="0" * 64, origin=ORIGIN_KIT)]
    )
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert not report.ok
    assert report.state == "missing"
    assert report.missing == ("a.mdc",)
    assert report.remediation == "ok sync"
    assert "a.mdc" in report.message


def test_missing_entries_are_sorted(tmp_path: Path) -> None:
    lock = _lock(
        [
            FootprintEntry(path="z.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
            FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
        ]
    )
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.missing == ("a.mdc", "z.mdc")


def test_preserved_origin_absent_is_never_missing(tmp_path: Path) -> None:
    """Frozen non-trigger: a preserved living doc is never existence-checked."""
    lock = _lock(
        [
            FootprintEntry(
                path="docs/ROADMAP.md", source="s", sha256="0" * 64, origin=ORIGIN_PRESERVED
            )
        ]
    )
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.ok
    assert report.state == "ok"
    assert report.missing == ()


def test_content_mismatch_is_never_missing(tmp_path: Path) -> None:
    """Frozen non-trigger: a file that exists but whose content differs is not this gate's job."""
    (tmp_path / "a.mdc").write_text("totally different content now", encoding="utf-8")
    lock = _lock(
        [FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)]
    )
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.ok
    assert report.state == "ok"


def test_empty_footprint_lock_is_ok(tmp_path: Path) -> None:
    """A lock declaring zero entries has nothing to check — vacuously ok."""
    report = check_footprint_integrity(tmp_path, lock=_lock([]))
    assert report.ok
    assert report.state == "ok"


def test_mixed_missing_and_preserved_only_flags_kit_owned(tmp_path: Path) -> None:
    (tmp_path / "present.mdc").write_text("x", encoding="utf-8")
    lock = _lock(
        [
            FootprintEntry(path="present.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
            FootprintEntry(path="absent.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
            FootprintEntry(
                path="docs/ROADMAP.md", source="s", sha256="0" * 64, origin=ORIGIN_PRESERVED
            ),
        ]
    )
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.state == "missing"
    assert report.missing == ("absent.mdc",)


def test_report_is_frozen_dataclass() -> None:
    report = FootprintIntegrityReport(state="ok", message="fine", remediation=None)
    assert report.ok
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.state = "missing"  # type: ignore[misc]

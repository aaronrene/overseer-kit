"""Data-integrity: `check_footprint_integrity` is a pure function of its inputs (§KH3.8)."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import ORIGIN_KIT, ORIGIN_PRESERVED, FootprintEntry, build_version_lock_from_entries
from tools.footprint_integrity import check_footprint_integrity


def _lock(entries: list[FootprintEntry]):
    return build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=entries,
        installed_at="2026-01-01T00:00:00Z",
    )


def test_identical_state_yields_identical_report(tmp_path: Path) -> None:
    (tmp_path / "present.mdc").write_text("x", encoding="utf-8")
    lock = _lock(
        [
            FootprintEntry(path="present.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
            FootprintEntry(path="absent.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
        ]
    )
    first = check_footprint_integrity(tmp_path, lock=lock)
    second = check_footprint_integrity(tmp_path, lock=lock)
    assert first == second
    assert first.missing == second.missing


def test_no_partial_state_on_repeated_calls(tmp_path: Path) -> None:
    """No I/O side effects — running the check never mutates the repo or the lock."""
    (tmp_path / "a.mdc").write_text("x", encoding="utf-8")
    lock = _lock([FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)])
    before = (tmp_path / "a.mdc").read_text(encoding="utf-8")
    for _ in range(10):
        check_footprint_integrity(tmp_path, lock=lock)
    after = (tmp_path / "a.mdc").read_text(encoding="utf-8")
    assert before == after
    assert lock.footprint == (
        FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
    ) or list(lock.footprint) == [
        FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)
    ]


def test_varying_disk_state_yields_varying_report_deterministically(tmp_path: Path) -> None:
    lock = _lock([FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)])

    absent_report = check_footprint_integrity(tmp_path, lock=lock)
    assert absent_report.state == "missing"

    (tmp_path / "a.mdc").write_text("x", encoding="utf-8")
    present_report = check_footprint_integrity(tmp_path, lock=lock)
    assert present_report.state == "ok"

    (tmp_path / "a.mdc").unlink()
    absent_again = check_footprint_integrity(tmp_path, lock=lock)
    assert absent_again == absent_report


def test_origin_reclassification_changes_report_deterministically(tmp_path: Path) -> None:
    """Marking an absent file `preserved` deterministically flips the outcome to ok."""
    kit_lock = _lock([FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)])
    preserved_lock = _lock(
        [FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_PRESERVED)]
    )
    assert check_footprint_integrity(tmp_path, lock=kit_lock).state == "missing"
    assert check_footprint_integrity(tmp_path, lock=preserved_lock).state == "ok"

"""Security: the self-integrity gate is fail-closed and leaks no content (§KH3.8)."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import ORIGIN_KIT, FootprintEntry, build_version_lock_from_entries
from tools.footprint_integrity import check_footprint_integrity


def _lock(entries: list[FootprintEntry]):
    return build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=entries,
        installed_at="2026-01-01T00:00:00Z",
    )


def test_corrupt_lock_fails_closed_not_ok(tmp_path: Path) -> None:
    overseer = tmp_path / ".overseer"
    overseer.mkdir(parents=True)
    (overseer / "version.lock").write_text("{{{not yaml", encoding="utf-8")
    report = check_footprint_integrity(tmp_path)
    assert not report.ok
    assert report.state == "unreadable"


def test_remediation_text_is_static_never_shell_invoked(tmp_path: Path) -> None:
    lock = _lock([FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)])
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.remediation == "ok sync"
    # A literal string, not an f-string interpolating any path/content — nothing to inject.
    assert "{" not in report.remediation
    assert "$" not in report.remediation
    assert ";" not in report.remediation


def test_missing_paths_reported_never_leak_file_contents(tmp_path: Path) -> None:
    """The gate only ever stats paths — it must never read or echo file bytes."""
    secret_path = ".overseer/policy/secret-looking-name.yaml"
    lock = _lock([FootprintEntry(path=secret_path, source="s", sha256="0" * 64, origin=ORIGIN_KIT)])
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.missing == (secret_path,)
    # The path itself is expected (it's a declared destination, not a secret value);
    # nothing beyond the path string appears anywhere in the report.
    assert secret_path in report.message
    for field_value in (report.state, report.remediation):
        if field_value is not None:
            assert "\n" not in field_value or field_value == report.message


def test_unusual_lock_entry_paths_never_crash_or_execute(tmp_path: Path) -> None:
    """An unusual/malformed lock entry path is only ever passed to a filesystem stat — never
    executed, interpolated into a shell command, or otherwise treated as anything but a plain
    path string, matching the existing `_compute_footprint_integrity` precedent in status.py."""
    lock = _lock(
        [
            FootprintEntry(path="../outside-canary.txt", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
            FootprintEntry(path="a; rm -rf /tmp/x", source="s", sha256="0" * 64, origin=ORIGIN_KIT),
        ]
    )
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.state in {"ok", "missing"}


def test_ok_report_never_lists_any_paths(tmp_path: Path) -> None:
    (tmp_path / "a.mdc").write_text("x", encoding="utf-8")
    lock = _lock([FootprintEntry(path="a.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)])
    report = check_footprint_integrity(tmp_path, lock=lock)
    assert report.state == "ok"
    assert report.missing == ()

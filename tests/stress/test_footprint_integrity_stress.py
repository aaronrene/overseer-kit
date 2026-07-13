"""Stress: `check_footprint_integrity` stays bounded with a large declared footprint (§KH3.8)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.version_lock import ORIGIN_KIT, FootprintEntry, build_version_lock_from_entries
from tools.footprint_integrity import check_footprint_integrity

ENTRY_COUNT = 5_000


def test_large_declared_footprint_resolves_in_bounded_time(tmp_path: Path) -> None:
    entries = [
        FootprintEntry(
            path=f"generated/file_{i:05d}.mdc",
            source=f"cursor/rules/file_{i:05d}.mdc",
            sha256="0" * 64,
            origin=ORIGIN_KIT,
        )
        for i in range(ENTRY_COUNT)
    ]
    # Half exist on disk, half do not — exercises both branches at scale.
    generated_dir = tmp_path / "generated"
    generated_dir.mkdir()
    for i in range(0, ENTRY_COUNT, 2):
        (generated_dir / f"file_{i:05d}.mdc").write_text("x", encoding="utf-8")

    lock = build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=entries,
        installed_at="2026-01-01T00:00:00Z",
    )

    started = time.monotonic()
    report = check_footprint_integrity(tmp_path, lock=lock)
    elapsed = time.monotonic() - started

    assert report.state == "missing"
    assert len(report.missing) == ENTRY_COUNT // 2
    # One Path.is_file() per entry only — no hashing, no per-file content read.
    assert elapsed < 5.0


def test_missing_count_scales_linearly_not_quadratically(tmp_path: Path) -> None:
    """A doubled entry count should not blow up runtime disproportionately (O(n), not O(n^2))."""
    def _time_for(count: int) -> float:
        entries = [
            FootprintEntry(path=f"f_{i}.mdc", source="s", sha256="0" * 64, origin=ORIGIN_KIT)
            for i in range(count)
        ]
        lock = build_version_lock_from_entries(
            kit_version="0.1.0",
            config_version=1,
            entries=entries,
            installed_at="2026-01-01T00:00:00Z",
        )
        started = time.monotonic()
        check_footprint_integrity(tmp_path, lock=lock)
        return time.monotonic() - started

    small = _time_for(500)
    large = _time_for(5_000)
    # Generous bound — guards against accidental quadratic behavior, not micro-timing noise.
    assert large < small * 50 + 1.0

"""Stress tests for LT loop tightening (§LT.10)."""

from __future__ import annotations

from pathlib import Path

from tests.support import FIXTURES, KIT_ROOT, git_status_runner, load_fixture_config, run_cli
from tools.footprint_coverage import check_footprint_coverage
from tools.handover_compact import compact_handover_change_log


def test_compact_200_bullets_keep_15(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    bullets = "\n\n".join(f"- **2026-01-01** — entry {i}" for i in range(200))
    handover.write_text(
        f"<!-- overseer:anchor:change-log -->\n{bullets}\n"
        "<!-- /overseer:anchor:change-log -->\n",
        encoding="utf-8",
    )
    report = compact_handover_change_log(config, tmp_path, keep=15, write=True)
    assert report.ok
    assert report.compacted == 185
    living = handover.read_text(encoding="utf-8")
    assert living.count("- **2026-01-01**") == 15
    archive = tmp_path / report.archive
    assert archive.is_file()
    assert archive.read_text(encoding="utf-8").count("- **2026-01-01**") == 185


def test_coverage_many_dests(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    from cli.footprint import resolve_footprint
    from cli.version_lock import ORIGIN_KIT, FootprintEntry, build_version_lock_from_entries

    files = resolve_footprint(config, kit=KIT_ROOT)
    assert len(files) >= 20
    entries = [
        FootprintEntry(path=f.destination, source=f.source, sha256="0" * 64, origin=ORIGIN_KIT)
        for f in files
    ]
    lock = build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=entries,
        installed_at="2026-01-01T00:00:00Z",
    )
    report = check_footprint_coverage(tmp_path, config, lock=lock, rendered=files, kit=KIT_ROOT)
    assert report.ok

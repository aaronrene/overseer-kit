"""Data-integrity tests for LT loop tightening (§LT.10)."""

from __future__ import annotations

from pathlib import Path

from tests.support import load_fixture_config, write_config
from tools.footprint_coverage import check_footprint_coverage
from tools.handover_compact import compact_handover_change_log


def test_compact_twice_second_no_op(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    bullets = "\n\n".join(f"- **2026-01-{day:02d}** — entry {day}" for day in range(1, 21))
    handover.write_text(
        f"<!-- overseer:anchor:change-log -->\n{bullets}\n"
        "<!-- /overseer:anchor:change-log -->\n",
        encoding="utf-8",
    )
    first = compact_handover_change_log(config, tmp_path, keep=15, write=True)
    archive = tmp_path / first.archive
    first_bytes = archive.read_bytes()
    second = compact_handover_change_log(config, tmp_path, keep=15, write=True)
    assert second.compacted == 0
    assert archive.read_bytes() == first_bytes


def test_coverage_does_not_rewrite_lock(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    lock_path = tmp_path / ".overseer" / "version.lock"
    lock_path.write_text("footprint: []\n", encoding="utf-8")
    before = lock_path.read_bytes()
    check_footprint_coverage(tmp_path, config)
    assert lock_path.read_bytes() == before


def test_dry_run_compact_writes_nothing(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    original = (
        "<!-- overseer:anchor:change-log -->\n"
        + "\n\n".join(f"- **2026-01-{d:02d}** — e" for d in range(1, 21))
        + "\n<!-- /overseer:anchor:change-log -->\n"
    )
    handover.write_text(original, encoding="utf-8")
    report = compact_handover_change_log(config, tmp_path, keep=15, write=False)
    assert report.compacted == 5
    assert handover.read_text(encoding="utf-8") == original
    assert not (tmp_path / "docs" / "archive" / "handover" / "CHANGE-LOG.md").exists()

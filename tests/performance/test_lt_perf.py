"""Performance tests for LT loop tightening (§LT.10)."""

from __future__ import annotations

import time
from pathlib import Path

from tests.support import KIT_ROOT, load_fixture_config
from tools.footprint_coverage import check_footprint_coverage
from tools.handover_compact import compact_handover_change_log


def test_coverage_and_compact_finish_quickly(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    bullets = "\n\n".join(f"- **2026-01-01** — entry {i}" for i in range(120))
    handover.write_text(
        f"# Handover\n\n<!-- overseer:anchor:change-log -->\n{bullets}\n"
        "<!-- /overseer:anchor:change-log -->\n",
        encoding="utf-8",
    )
    start = time.monotonic()
    for _ in range(20):
        check_footprint_coverage(tmp_path, config, kit=KIT_ROOT)
        compact_handover_change_log(config, tmp_path, keep=15, write=False)
    elapsed = time.monotonic() - start
    assert elapsed < 5.0

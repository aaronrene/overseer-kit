"""Performance — scaffold completes within a local budget."""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

from tools.check_ok.scaffold import scaffold_side_check


def test_scaffold_under_budget(tmp_path: Path) -> None:
    start = time.perf_counter()
    for i in range(20):
        scaffold_side_check(tmp_path, topic=f"perf-{i}", today=date(2026, 7, 17))
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0

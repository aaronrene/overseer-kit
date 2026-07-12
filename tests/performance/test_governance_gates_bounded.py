"""Performance bounds for governance gate scan."""

from __future__ import annotations

import time
from pathlib import Path

from adapters.config import load_config
from tests.support import FIXTURES
from tools.governance_gates import scan_governance_gates


def test_gate_scan_completes_within_bound(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-governance-gates.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    rows = ["| Phase | Model | Status | Deliverable |", "| --- | --- | --- | --- |"]
    rows.extend(
        f"| **K{index}** | Auto | **WIP** | slice {index} |" for index in range(100)
    )
    (docs / "ROADMAP.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (docs / "OVERSEER-HANDOVER.md").write_text("| **ID** | **K0** |\n", encoding="utf-8")

    start = time.perf_counter()
    scan_governance_gates(config, tmp_path)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0

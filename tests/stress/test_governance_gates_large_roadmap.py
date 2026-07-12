"""Stress tests for governance gate scan on large roadmap tables."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from tests.support import FIXTURES
from tools.governance_gates import scan_governance_gates


def test_large_roadmap_scan_bounded(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-governance-gates.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    rows = ["| Phase | Model | Status | Deliverable |", "| --- | --- | --- | --- |"]
    for index in range(500):
        rows.append(
            f"| **K{index} slice** | Auto | **DONE** | shipped slice {index} |"
        )
    rows.append("| **Active Auto** | Auto | **WIP** | `docs/PHASE-ACTIVE.md` pending |")
    (docs / "ROADMAP.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "| **ID** | **Active Auto** |\n",
        encoding="utf-8",
    )
    (docs / "PHASE-ACTIVE.md").write_text("not frozen\n", encoding="utf-8")

    result = scan_governance_gates(config, tmp_path)
    assert any(gate.phase_id == "Active Auto" for gate in result.pending)

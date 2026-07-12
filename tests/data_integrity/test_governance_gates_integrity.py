"""Data-integrity tests for governance gate scan idempotency."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from tests.support import FIXTURES
from tools.governance_gates import scan_governance_gates


def _seed(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-governance-gates.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-gates-roadmap.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-gates-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "PHASE-DEMO-THINKING.md").write_text(
        (FIXTURES / "governance-gates-phase-thinking.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return config


def test_scan_is_deterministic(tmp_path: Path) -> None:
    config = _seed(tmp_path)
    first = scan_governance_gates(config, tmp_path)
    second = scan_governance_gates(config, tmp_path)
    assert first.pending == second.pending
    assert first.active_phases == second.active_phases

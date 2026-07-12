"""Unit tests for governance gate reminders (§KH1.9)."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import ConfigError, load_config
from tests.support import FIXTURES
from tools.governance_gates import scan_governance_gates
from tools.governance_gates.checklist import governance_gates_checklist_lines


def test_config_parses_governance_gates_defaults() -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    assert config.governance_gates.remind is True
    assert config.governance_gates.freeze_review_required is True
    assert config.governance_gates.build_verification_required is True


def test_config_parses_governance_gates_explicit() -> None:
    config = load_config(FIXTURES / "config-governance-gates.yaml")
    assert config.governance_gates.remind is True
    assert "status" in config.governance_gates.surfaces
    assert "handover-paste" in config.governance_gates.surfaces


def test_config_rejects_unknown_governance_gates_key() -> None:
    with pytest.raises(ConfigError):
        load_config(FIXTURES / "config-governance-gates-bad.yaml")


def test_scan_detects_pending_freeze_review_and_build_verification(tmp_path: Path) -> None:
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

    result = scan_governance_gates(config, tmp_path)
    gate_ids = {gate.gate_id for gate in result.pending}
    assert "freeze_review" in gate_ids
    assert "build_verification" in gate_ids


def test_scan_suppressed_when_remind_false(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-governance-gates-suppressed.yaml")
    result = scan_governance_gates(config, tmp_path)
    assert result.suppressed is True
    assert result.pending == ()


def test_checklist_lines_include_invoke_commands() -> None:
    lines = governance_gates_checklist_lines()
    joined = "\n".join(lines)
    assert "freeze-review-loop" in joined
    assert "build-verification-review" in joined

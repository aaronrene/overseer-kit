"""Unit tests for ChecklistEngine semantics (K5b-r F1)."""

from __future__ import annotations

from pathlib import Path

from tools.freeze_reviewer.checklist import builtin_checklist
from tools.freeze_reviewer.providers.base import ChecklistEngine


def test_normative_escalation_vocabulary_is_not_a_finding() -> None:
    """Discussing security / tier-3 / billing must not auto-escalate (§K5.5 / §6.3)."""
    text = """
# Freeze contract

```yaml
phase: K5a
outputs:
  - id: contract
    path: docs/CONTRACT.md
    frozen: true
```

This document defines security, injection, irreversible deletes, real money billing,
live model spend, gates_tier3, and merge to main. Human escalation is rare and meaningful.
It includes a seven-tier test matrix and requires file+line citations.
"""
    findings = ChecklistEngine().evaluate(
        artifact_text=text,
        artifact_path="docs/CONTRACT.md",
        checklist=builtin_checklist(),
    )
    escalation_cats = {"security", "irreversible", "real_money", "gates_tier3"}
    assert not any(item.category in escalation_cats for item in findings)
    assert not any(item.check in {"C4", "C5", "C6", "C7"} for item in findings)


def test_absolute_path_still_emits_c4_security() -> None:
    text = (
        "# x\n\n```yaml\nphase: K\noutputs:\n  - id: a\n    path: docs/a.md\n"
        "    frozen: true\n```\n\nPath: /Users/operator/secret/repo\n"
        "seven-tier matrix and file+line discipline.\n"
    )
    findings = ChecklistEngine().evaluate(
        artifact_text=text,
        artifact_path="docs/x.md",
        checklist=builtin_checklist(),
    )
    assert any(item.check == "C4" and item.category == "security" for item in findings)


def test_k5_contract_dogfood_has_no_false_escalation() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "docs" / "PHASE-K5-FREEZE-REVIEWER-CONTRACT.md").read_text(encoding="utf-8")
    findings = ChecklistEngine().evaluate(
        artifact_text=text,
        artifact_path="docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md",
        checklist=builtin_checklist(),
    )
    escalation_cats = {"security", "irreversible", "real_money", "gates_tier3"}
    assert not any(item.category in escalation_cats for item in findings)

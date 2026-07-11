"""Unit tests for findings, verdicts, citations (§K5.6)."""

from __future__ import annotations

from tools.freeze_reviewer.findings import (
    assign_finding_ids,
    derive_verdict,
    validate_and_repair_findings,
    verdict_exit_code,
)
from tools.freeze_reviewer.types import Finding


def test_zero_findings_pass() -> None:
    assert derive_verdict([], human_escalation=["security"]) == "pass"
    assert verdict_exit_code("pass") == 0


def test_major_only_findings() -> None:
    findings = [
        Finding(check="C1", severity="MAJOR", category="completeness", path="docs/a.md", line=2, message="x").with_citation()
    ]
    assert derive_verdict(findings, human_escalation=["security"]) == "findings"
    assert verdict_exit_code("findings") == 7


def test_blocker_blocked() -> None:
    findings = [
        Finding(check="C2", severity="BLOCKER", category="completeness", path="docs/a.md", line=1, message="x").with_citation()
    ]
    assert derive_verdict(findings, human_escalation=[]) == "blocked"
    assert verdict_exit_code("blocked") == 8


def test_escalation_category_blocked_even_if_major() -> None:
    findings = [
        Finding(check="C4", severity="MAJOR", category="security", path="docs/a.md", line=3, message="x").with_citation()
    ]
    assert derive_verdict(findings, human_escalation=["security"]) == "blocked"


def test_uncited_finding_becomes_synthetic_blocked() -> None:
    raw = [Finding(check="C1", severity="MAJOR", category="other", path="", line=0, message="bad")]
    repaired = validate_and_repair_findings(raw, artifact_path="docs/a.md")
    assert repaired[0].severity == "BLOCKER"
    assert repaired[0].citation == "docs/a.md:1"


def test_stable_sort_and_ids() -> None:
    findings = [
        Finding(check="C2", severity="MINOR", category="other", path="docs/b.md", line=1, message="b").with_citation(),
        Finding(check="C1", severity="MAJOR", category="other", path="docs/a.md", line=5, message="a").with_citation(),
    ]
    assigned = assign_finding_ids(findings)
    assert [item.id for item in assigned] == ["F1", "F2"]
    assert assigned[0].path == "docs/a.md"

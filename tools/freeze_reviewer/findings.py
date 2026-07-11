"""Finding validation, stable sort, and verdict derivation (§K5.6)."""

from __future__ import annotations

from tools.freeze_reviewer.types import Finding, Verdict

SEVERITY_RANK = {"BLOCKER": 3, "MAJOR": 2, "MINOR": 1}

SYNTHETIC_UNCITED_MESSAGE = (
    "Reviewer engine emitted an invalid finding (missing or mismatched citation)."
)


def stable_sort_findings(findings: list[Finding]) -> list[Finding]:
    """Sort findings per §K5.6 stable sort rule."""
    return sorted(
        findings,
        key=lambda item: (
            item.path,
            item.line,
            -SEVERITY_RANK.get(item.severity, 0),
            item.check,
            item.message,
        ),
    )


def assign_finding_ids(findings: list[Finding]) -> list[Finding]:
    """Assign F1..Fn after stable sort."""
    sorted_items = stable_sort_findings(findings)
    for index, finding in enumerate(sorted_items, start=1):
        finding.id = f"F{index}"
    return sorted_items


def validate_and_repair_findings(
    findings: list[Finding],
    *,
    artifact_path: str,
) -> list[Finding]:
    """Enforce citation hard rule; synthesize blocked finding on violation."""
    repaired: list[Finding] = []
    for finding in findings:
        if finding.is_valid_citation():
            repaired.append(finding)
            continue
        repaired.append(
            Finding(
                check="OTHER",
                severity="BLOCKER",
                category="other",
                path=artifact_path,
                line=1,
                message=SYNTHETIC_UNCITED_MESSAGE,
            ).with_citation()
        )
    return assign_finding_ids(repaired)


def derive_verdict(
    findings: list[Finding],
    *,
    human_escalation: list[str],
) -> Verdict:
    """Map findings to pass | findings | blocked."""
    if not findings:
        return "pass"
    escalation = set(human_escalation)
    for finding in findings:
        if finding.category in escalation:
            return "blocked"
    for finding in findings:
        if finding.severity == "BLOCKER":
            return "blocked"
    return "findings"


def verdict_exit_code(verdict: Verdict) -> int:
    """Map verdict to review-specific exit code."""
    if verdict == "pass":
        return 0
    if verdict == "findings":
        return 7
    return 8

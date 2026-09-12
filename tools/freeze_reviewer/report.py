"""§K5.9 / §FRV report payload and stdout rendering."""

from __future__ import annotations

from typing import Any

from adapters.config import FreezeContractConfig
from tools.freeze_reviewer.engine import HUMAN_INSTRUCTIONS, resolve_exit_code
from tools.freeze_reviewer.types import Finding, ReviewResult, ReviewerSettings

HUMAN_INSTRUCTIONS_TEXT = HUMAN_INSTRUCTIONS


def reviewer_payload(settings: ReviewerSettings, config: FreezeContractConfig) -> dict[str, Any]:
    """Reviewer section for JSON report."""
    if settings.mode == "human":
        return {
            "mode": "human",
            "model": config.reviewer.model,
            "provider": config.reviewer.provider,
            "fallback": config.reviewer.fallback,
        }
    return {
        "mode": settings.mode,
        "model": settings.model,
        "provider": settings.provider,
        "fallback": settings.fallback,
    }


def finding_to_dict(finding: Finding) -> dict[str, Any]:
    return {
        "id": finding.id,
        "check": finding.check,
        "severity": finding.severity,
        "category": finding.category,
        "path": finding.path,
        "line": finding.line,
        "message": finding.message,
        "citation": finding.citation,
    }


def build_report(
    *,
    freeze_path: str,
    result: ReviewResult,
    reviewer: ReviewerSettings,
    config: FreezeContractConfig,
    enabled: bool,
) -> dict[str, Any]:
    """Build the unified §K5.9 / §FRV report object."""
    exit_code = resolve_exit_code(result, refused=result.refused)
    stamp_payload = result.stamp.to_mapping() if result.stamp else None
    reason: str | None
    if result.escalation_refused:
        reason = result.escalation_refuse_cause or "stamp_escalation_refused"
    else:
        reason = result.reason
    payload: dict[str, Any] = {
        "command": "review",
        "freeze": freeze_path,
        "gate": "mechanical",
        "verdict": result.verdict,
        "mechanical_verdict": result.verdict if result.stamp else result.verdict,
        "exit_code": exit_code,
        "escalation": result.escalation,
        "reason": reason,
        "provider_cause": result.provider_cause,
        "checklist": list(result.checklist_ids),
        "instructions": HUMAN_INSTRUCTIONS_TEXT if result.escalation == "human" else None,
        "enabled": enabled,
        "declaration": result.declaration,
        "reviewer": reviewer_payload(reviewer, config),
        "findings": [finding_to_dict(item) for item in result.findings],
        "stamp": stamp_payload,
        "dry_run": result.dry_run,
        "operator_block": result.operator_block,
        "escalation_refused": result.escalation_refused,
    }
    if result.escalation_refused:
        payload["existing_verdict"] = result.existing_stamp_verdict
    return payload


def render_human_report(*, freeze_path: str, result: ReviewResult) -> str:
    """Render human stdout per §K5.9 / §FRV.3.5."""
    lines = [f"Freeze review: {freeze_path}"]
    # Mechanical pass runs: Gate + Mechanical verdict (never bare "Verdict:")
    if result.stamp is not None or (result.verdict == "pass" and not result.escalation):
        lines.append("Gate: mechanical")
        lines.append(f"Mechanical verdict: {result.verdict}")
    else:
        lines.append(f"Verdict: {result.verdict}")
    lines.append(f"Findings ({len(result.findings)}):")
    for finding in result.findings:
        lines.append(
            f"  {finding.id} {finding.severity} {finding.category} "
            f"{finding.citation}  {finding.message}"
        )
    if result.escalation == "human":
        lines.append("Escalation: human")
        lines.append(f"Reason: {result.reason}")
        cause = result.provider_cause or "(none)"
        lines.append(f"Provider cause: {cause}")
        lines.append(f"Checklist: {', '.join(result.checklist_ids)}")
        lines.append(f"Instructions: {HUMAN_INSTRUCTIONS_TEXT}")
    else:
        lines.append("Escalation: none")
    if result.escalation_refused:
        existing = result.existing_stamp_verdict or "(unknown)"
        lines.append(
            f"Notice: stamp_escalation_refused — existing mechanical verdict is {existing}"
        )
    if result.operator_block is True:
        lines.append("Operator block: auto_may_start is not true (Auto authorization blocked)")
    if result.verdict == "pass" and result.stamp and result.escalation_refused:
        lines.append("Stamp: (not written — stamp_escalation_refused)")
    elif result.verdict == "pass" and result.stamp and not result.dry_run and result.stamp_written:
        lines.append("Stamp: written")
    elif result.verdict == "pass" and result.stamp and result.dry_run:
        lines.append("Stamp: (dry-run — would write)")
    elif result.verdict == "pass" and result.stamp and result.no_stamp:
        lines.append("Stamp: (not written — no-stamp)")
    elif result.verdict == "pass" and result.stamp and not result.stamp_written:
        lines.append("Stamp: (unchanged — idempotent)")
    else:
        lines.append("Stamp: (not written — verdict != pass)")
    return "\n".join(lines)

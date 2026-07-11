"""§K5.9 report payload and stdout rendering."""

from __future__ import annotations

from typing import Any

from adapters.config import FreezeContractConfig
from tools.freeze_reviewer.engine import HUMAN_INSTRUCTIONS
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
    """Build the unified §K5.9 report object."""
    exit_code = 8 if result.escalation == "human" else (
        7 if result.verdict == "findings" else (0 if result.verdict == "pass" else 8)
    )
    stamp_payload = result.stamp.to_mapping() if result.stamp else None
    return {
        "command": "review",
        "freeze": freeze_path,
        "verdict": result.verdict,
        "exit_code": exit_code,
        "escalation": result.escalation,
        "reason": result.reason,
        "provider_cause": result.provider_cause,
        "checklist": list(result.checklist_ids),
        "instructions": HUMAN_INSTRUCTIONS_TEXT if result.escalation == "human" else None,
        "enabled": enabled,
        "declaration": result.declaration,
        "reviewer": reviewer_payload(reviewer, config),
        "findings": [finding_to_dict(item) for item in result.findings],
        "stamp": stamp_payload,
        "dry_run": result.dry_run,
    }


def render_human_report(*, freeze_path: str, result: ReviewResult) -> str:
    """Render human stdout per §K5.9."""
    lines = [f"Freeze review: {freeze_path}", f"Verdict: {result.verdict}"]
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
    if result.verdict == "pass" and result.stamp and not result.dry_run and result.stamp_written:
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

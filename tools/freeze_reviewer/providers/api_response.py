"""Parse headless API review responses into findings (§K5.6)."""

from __future__ import annotations

import json
from typing import Any

from tools.freeze_reviewer.types import Category, Finding, Severity

VALID_SEVERITIES = frozenset({"BLOCKER", "MAJOR", "MINOR"})
VALID_CATEGORIES = frozenset(
    {
        "security",
        "irreversible",
        "real_money",
        "gates_tier3",
        "completeness",
        "consistency",
        "other",
    }
)


class ProviderReviewError(Exception):
    """Raised when the API provider returns an invalid or failed review response."""


def parse_review_response(payload: bytes, *, default_path: str) -> list[Finding]:
    """Parse a /review JSON response into pre-validation findings."""
    try:
        raw = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderReviewError("invalid JSON response from review API") from exc
    if not isinstance(raw, dict):
        raise ProviderReviewError("review API response root must be a mapping")
    findings_raw = raw.get("findings")
    if findings_raw is None:
        return []
    if not isinstance(findings_raw, list):
        raise ProviderReviewError("review API findings must be a list")
    findings: list[Finding] = []
    for index, entry in enumerate(findings_raw):
        finding = _parse_finding_entry(entry, index=index, default_path=default_path)
        findings.append(finding.with_citation())
    return findings


def _parse_finding_entry(entry: Any, *, index: int, default_path: str) -> Finding:
    if not isinstance(entry, dict):
        raise ProviderReviewError(f"findings[{index}] must be a mapping")
    check = entry.get("check")
    severity = entry.get("severity")
    category = entry.get("category")
    path = entry.get("path")
    line = entry.get("line")
    message = entry.get("message")
    if not isinstance(check, str) or not check.strip():
        raise ProviderReviewError(f"findings[{index}].check must be a non-empty string")
    if severity not in VALID_SEVERITIES:
        raise ProviderReviewError(
            f"findings[{index}].severity must be BLOCKER|MAJOR|MINOR"
        )
    if category not in VALID_CATEGORIES:
        raise ProviderReviewError(f"findings[{index}].category is invalid")
    if not isinstance(path, str) or not path.strip():
        path = default_path
    if not isinstance(line, int) or line < 1:
        line = 1
    if not isinstance(message, str) or not message.strip():
        raise ProviderReviewError(f"findings[{index}].message must be a non-empty string")
    return Finding(
        check=check,
        severity=severity,  # type: ignore[arg-type]
        category=category,  # type: ignore[arg-type]
        path=path,
        line=line,
        message=message,
    )

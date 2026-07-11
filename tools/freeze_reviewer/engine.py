"""Freeze review orchestration (§K5.2 steps 6–12)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.config import FreezeContractConfig, OverseerConfig
from tools.freeze_reviewer.artifact import parse_artifact
from tools.freeze_reviewer.checklist import builtin_checklist
from tools.freeze_reviewer.findings import (
    derive_verdict,
    validate_and_repair_findings,
    verdict_exit_code,
)
from tools.freeze_reviewer.providers.base import ReviewProvider, provider_for
from tools.freeze_reviewer.stamp import build_stamp, write_stamp_or_fail
from tools.freeze_reviewer.types import ChecklistItem, ReviewResult, ReviewerSettings

HUMAN_INSTRUCTIONS = (
    "Perform Freeze-Step Review per SPEC §6; cite file+line for every finding; "
    "record verdict in the artifact review record."
)


@dataclass
class ReviewOptions:
    """Per-invocation review options."""

    dry_run: bool = False
    no_stamp: bool = False
    mode: str | None = None
    provider: str | None = None
    model: str | None = None
    checklist: list[ChecklistItem] | None = None
    kit_version: str = "0.1.0"
    injected_provider: ReviewProvider | None = None


def resolve_reviewer_settings(
    config: FreezeContractConfig,
    options: ReviewOptions,
) -> ReviewerSettings:
    """Resolve CLI overrides > config > defaults."""
    mode = options.mode or config.reviewer.mode
    if mode == "human":
        return ReviewerSettings(mode="human", model=None, provider=None, fallback=None)
    model = options.model or config.reviewer.model
    provider = options.provider or config.reviewer.provider
    fallback = config.reviewer.fallback
    return ReviewerSettings(mode=mode, model=model, provider=provider, fallback=fallback)


def run_freeze_review(
    *,
    artifact_path: Path,
    rel_path: str,
    config: OverseerConfig,
    options: ReviewOptions,
) -> ReviewResult:
    """Execute the freeze review pipeline."""
    checklist = options.checklist or builtin_checklist()
    checklist_ids = [item.id for item in checklist]
    result = ReviewResult(checklist_ids=checklist_ids)

    if not config.freeze_contract.enabled:
        result.refused = True
        result.refuse_cause = "freeze_contract.enabled is false"
        result.verdict = "blocked"
        return result

    try:
        parsed = parse_artifact(artifact_path, rel_path=rel_path)
    except ValueError as exc:
        if str(exc) == "not-utf8":
            result.refused = True
            result.refuse_cause = "not-utf8"
            result.verdict = "blocked"
            return result
        raise

    result.declaration = parsed.declaration
    result.artifact_kind = parsed.kind
    result.dry_run = options.dry_run
    result.no_stamp = options.no_stamp
    reviewer = resolve_reviewer_settings(config.freeze_contract, options)

    if reviewer.mode == "human":
        result.verdict = "blocked"
        result.escalation = "human"
        result.reason = "mode_human"
        return result

    provider = provider_for(reviewer, options.injected_provider)
    reachable, cause = provider.reachable()
    if not reachable:
        result.verdict = "blocked"
        result.escalation = "human"
        result.reason = "provider_unreachable"
        result.provider_cause = cause
        return result

    raw_findings = provider.review(
        artifact_text=parsed.text,
        artifact_path=rel_path,
        checklist=checklist,
        reviewer=reviewer,
    )
    findings = validate_and_repair_findings(raw_findings, artifact_path=rel_path)
    result.findings = findings
    result.verdict = derive_verdict(findings, human_escalation=config.freeze_contract.human_escalation)

    if result.verdict == "pass":
        stamp = build_stamp(parsed, reviewer=reviewer, kit_version=options.kit_version)
        result.stamp = stamp
        if not options.dry_run and not options.no_stamp:
            written, io_failed = write_stamp_or_fail(artifact_path, parsed, stamp)
            result.stamp_written = written
            result.io_error = io_failed

    return result


def resolve_exit_code(result: ReviewResult, *, config_error: bool = False, refused: bool = False) -> int:
    """Apply frozen precedence 2>4>5>8>7>0."""
    if config_error:
        return 2
    if refused or result.refused:
        return 4
    if result.io_error:
        return 5
    if result.escalation == "human" or result.verdict == "blocked":
        return 8
    if result.verdict == "findings":
        return 7
    if result.verdict == "pass":
        return 0
    return verdict_exit_code(result.verdict)

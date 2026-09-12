"""Freeze review orchestration (§K5.2 steps 6–12 / §FRV)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.config import FreezeContractConfig, OverseerConfig
from tools.freeze_authorization.resolve import resolve_stamp_record
from tools.freeze_reviewer.artifact import extract_existing_stamp, parse_artifact
from tools.freeze_reviewer.checklist import builtin_checklist
from tools.freeze_reviewer.findings import (
    derive_verdict,
    validate_and_repair_findings,
    verdict_exit_code,
)
from tools.freeze_reviewer.providers.api_response import ProviderReviewError
from tools.freeze_reviewer.providers.base import ReviewProvider, provider_for
from tools.freeze_reviewer.stamp import build_stamp, write_stamp_or_fail
from tools.freeze_reviewer.types import ChecklistItem, ReviewResult, ReviewerSettings

HUMAN_INSTRUCTIONS = (
    "Perform Freeze-Step Review per SPEC §6; cite file+line for every finding; "
    "record verdict in the artifact review record."
)

EXIT_STAMP_ESCALATION_REFUSED = 39


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
    kit_root: Path | None = None
    injected_provider: ReviewProvider | None = None
    override_non_pass_stamp: bool = False
    checklist_source: str = "builtin"


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


def _read_operator_block(parsed) -> bool | None:
    """Return operator_block report value from freeze mapping (§FRV.8.3)."""
    mapping = parsed.freeze_mapping
    if not isinstance(mapping, dict) or "auto_may_start" not in mapping:
        return None
    val = mapping.get("auto_may_start")
    if val is True:
        return False
    return True


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
    result.operator_block = _read_operator_block(parsed)
    reviewer = resolve_reviewer_settings(config.freeze_contract, options)

    if reviewer.mode == "human":
        result.verdict = "blocked"
        result.escalation = "human"
        result.reason = "mode_human"
        return result

    provider = provider_for(reviewer, options.injected_provider, kit_root=options.kit_root)
    reachable, cause = provider.reachable()
    if not reachable:
        result.verdict = "blocked"
        result.escalation = "human"
        result.reason = "provider_unreachable"
        result.provider_cause = cause
        return result

    try:
        raw_findings = provider.review(
            artifact_text=parsed.text,
            artifact_path=rel_path,
            checklist=checklist,
            reviewer=reviewer,
        )
    except ProviderReviewError as exc:
        result.verdict = "blocked"
        result.escalation = "human"
        result.reason = "provider_unreachable"
        result.provider_cause = str(exc)
        return result

    # §FRV.4.2 — producer_identity AFTER review()
    identity_fn = getattr(provider, "producer_identity", None)
    if callable(identity_fn):
        produced_by, provider_kind = identity_fn()
    else:
        produced_by, provider_kind = ("unknown", "rule_engine")

    findings = validate_and_repair_findings(raw_findings, artifact_path=rel_path)
    result.findings = findings
    result.verdict = derive_verdict(findings, human_escalation=config.freeze_contract.human_escalation)

    if result.verdict == "pass":
        existing = extract_existing_stamp(parsed)
        resolved = resolve_stamp_record(existing) if existing else None
        existing_verdict = (
            resolved.verdict if resolved is not None and resolved.kind == "mechanical" else None
        )
        refuse_escalation = (
            existing_verdict is not None
            and existing_verdict != ""
            and existing_verdict != "pass"
            and not options.override_non_pass_stamp
        )
        if refuse_escalation:
            result.escalation_refused = True
            result.escalation_refuse_cause = "stamp_escalation_refused"
            result.existing_stamp_verdict = existing_verdict
            stamp = build_stamp(
                parsed,
                reviewer=reviewer,
                kit_version=options.kit_version,
                produced_by=produced_by,
                provider_kind=provider_kind,
                checklist_ids=checklist_ids,
                checklist_source=options.checklist_source,
                findings_count=len(findings),
                override_applied=False,
            )
            result.stamp = stamp
            return result

        override_applied = bool(
            options.override_non_pass_stamp
            and existing_verdict
            and existing_verdict != "pass"
        )
        stamp = build_stamp(
            parsed,
            reviewer=reviewer,
            kit_version=options.kit_version,
            produced_by=produced_by,
            provider_kind=provider_kind,
            checklist_ids=checklist_ids,
            checklist_source=options.checklist_source,
            findings_count=len(findings),
            override_applied=override_applied,
        )
        result.stamp = stamp
        if not options.dry_run and not options.no_stamp:
            written, io_failed = write_stamp_or_fail(artifact_path, parsed, stamp)
            result.stamp_written = written
            result.io_error = io_failed

    return result


def resolve_exit_code(result: ReviewResult, *, config_error: bool = False, refused: bool = False) -> int:
    """Apply frozen precedence 2 > 4 > 5 > 39 > 8 > 7 > 0 (§FRV.5.2 / §FRV.10)."""
    if config_error:
        return 2
    if refused or result.refused:
        return 4
    if result.io_error:
        return 5
    if result.escalation_refused and not result.dry_run and not result.no_stamp:
        return EXIT_STAMP_ESCALATION_REFUSED
    if result.escalation == "human" or result.verdict == "blocked":
        return 8
    if result.verdict == "findings":
        return 7
    if result.verdict == "pass":
        return 0
    return verdict_exit_code(result.verdict)

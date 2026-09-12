"""Review stamp write path (§K5.7 / §FRV.3–§FRV.5)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cli.atomic import WriteFailure, atomic_write_text
from tools.freeze_authorization.resolve import resolve_stamp_record
from tools.freeze_reviewer.artifact import (
    STAMP_MARKER,
    ParsedArtifact,
    _operator_forced_md_prefix,
    artifact_digest,
    extract_existing_stamp,
    pre_stamp_canonical_bytes,
)
from tools.freeze_reviewer.serializer import dump_freeze_mapping
from tools.freeze_reviewer.types import (
    CLI_OWNED_STAMP_KEYS,
    STAMP_KEY_ORDER,
    ReviewStamp,
    ReviewerSettings,
)


def utc_now_z() -> str:
    """Return ISO-8601 UTC timestamp with trailing Z."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_stamp(
    parsed: ParsedArtifact,
    *,
    reviewer: ReviewerSettings,
    kit_version: str,
    produced_by: str,
    provider_kind: str,
    checklist_ids: list[str],
    checklist_source: str,
    findings_count: int,
    override_applied: bool = False,
) -> ReviewStamp:
    """Build a fourteen-key mechanical stamp; never emit ``verdict`` (§FRV.3–§FRV.4)."""
    model = None if provider_kind == "rule_engine" else reviewer.model
    return ReviewStamp(
        reviewed_at=utc_now_z(),
        mechanical_verdict="pass",
        reviewer_mode=reviewer.mode,
        reviewer_model=model,
        reviewer_provider=reviewer.provider,
        kit_version=kit_version,
        artifact_digest=artifact_digest(parsed),
        gate="mechanical",
        produced_by=produced_by,
        provider_kind=provider_kind,
        checklist_ids=list(checklist_ids),
        checklist_source=checklist_source,
        findings_count=findings_count,
        override_applied=override_applied,
    )


def merge_stamp_mapping(existing: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    """Merge per §FRV.5.1: fourteen CLI keys from N, then unknown keys from E; drop legacy verdict."""
    e = existing if isinstance(existing, dict) else {}
    merged: dict[str, Any] = {}
    for key in STAMP_KEY_ORDER:
        if key in new:
            merged[key] = new[key]
    for key, value in e.items():
        if key in CLI_OWNED_STAMP_KEYS:
            continue
        if key not in merged:
            merged[key] = value
    return merged


def stamp_is_idempotent_noop(parsed: ParsedArtifact, new_stamp: ReviewStamp) -> bool:
    """True when re-run is a no-op per §FRV.5.3 four conditions."""
    existing = extract_existing_stamp(parsed)
    if not existing:
        return False
    resolved = resolve_stamp_record(existing)
    if resolved.kind != "mechanical":
        return False
    if resolved.verdict != new_stamp.mechanical_verdict:
        return False
    if existing.get("artifact_digest") != new_stamp.artifact_digest:
        return False
    # Condition 4: preserve existing reviewed_at so a true no-op does not refresh it.
    candidate = new_stamp.to_mapping()
    if "reviewed_at" in existing and existing["reviewed_at"] is not None:
        candidate["reviewed_at"] = existing["reviewed_at"]
    from dataclasses import replace

    compare_stamp = replace(
        new_stamp,
        reviewed_at=str(candidate["reviewed_at"]),
        override_applied=bool(candidate.get("override_applied", False)),
    )
    # Align compare_stamp fields with candidate for merge fidelity
    compare_stamp = replace(
        compare_stamp,
        gate=str(candidate.get("gate", "mechanical")),
        produced_by=str(candidate.get("produced_by", compare_stamp.produced_by)),
        provider_kind=str(candidate.get("provider_kind", compare_stamp.provider_kind)),
        checklist_ids=list(candidate.get("checklist_ids") or []),
        checklist_source=str(candidate.get("checklist_source", compare_stamp.checklist_source)),
        findings_count=int(candidate.get("findings_count") or 0),
    )
    rendered = render_stamped_text(parsed, compare_stamp)
    return rendered == parsed.text


def _insert_review_stamp(mapping: dict, stamp: ReviewStamp) -> dict:
    updated = dict(mapping)
    existing = mapping.get("review_stamp") if isinstance(mapping.get("review_stamp"), dict) else {}
    updated["review_stamp"] = merge_stamp_mapping(existing, stamp.to_mapping())
    return updated


def render_stamped_text(parsed: ParsedArtifact, stamp: ReviewStamp) -> str:
    """Render artifact text with the stamp applied."""
    if parsed.kind == "markdown_fence" and parsed.freeze_mapping is not None and parsed.fence_match:
        updated = _insert_review_stamp(parsed.freeze_mapping, stamp)
        serialized = dump_freeze_mapping(updated)
        start, end = parsed.fence_match.span()
        fence_lang = parsed.fence_match.group(1)
        return parsed.text[:start] + f"```{fence_lang}\n{serialized}```" + parsed.text[end:]

    if parsed.kind == "yaml_whole" and parsed.freeze_mapping is not None:
        updated = _insert_review_stamp(parsed.freeze_mapping, stamp)
        return dump_freeze_mapping(updated)

    if parsed.kind == "operator_forced_md":
        existing = extract_existing_stamp(parsed) or {}
        merged = merge_stamp_mapping(existing, stamp.to_mapping())
        stamp_yaml = dump_freeze_mapping({"review_stamp": merged})
        marker_index = parsed.text.rfind(STAMP_MARKER)
        if marker_index == -1:
            base = parsed.text if parsed.text.endswith("\n") else parsed.text + "\n"
        else:
            base = _operator_forced_md_prefix(parsed.text)
        return f"{base}\n{STAMP_MARKER}\n```yaml\n{stamp_yaml}```"

    if parsed.kind == "operator_forced_yaml":
        base = parsed.freeze_mapping if isinstance(parsed.freeze_mapping, dict) else {}
        updated = _insert_review_stamp(base, stamp)
        return dump_freeze_mapping(updated)

    return parsed.text


def write_stamp(
    path: Path,
    parsed: ParsedArtifact,
    stamp: ReviewStamp,
) -> bool:
    """Atomically write stamp; return False when idempotent no-op."""
    if stamp_is_idempotent_noop(parsed, stamp):
        return False
    text = render_stamped_text(parsed, stamp)
    atomic_write_text(path, text)
    return True


def write_stamp_or_fail(path: Path, parsed: ParsedArtifact, stamp: ReviewStamp) -> tuple[bool, bool]:
    """Write stamp; return (written, io_failed)."""
    try:
        written = write_stamp(path, parsed, stamp)
        return written, False
    except WriteFailure:
        return False, True


def reference_digest(parsed: ParsedArtifact) -> str:
    """Independently compute digest reference for data-integrity tests."""
    digest_hex = __import__("hashlib").sha256(pre_stamp_canonical_bytes(parsed)).hexdigest()
    return f"sha256:{digest_hex}"

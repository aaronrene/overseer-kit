"""Review stamp write path (§K5.7)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cli.atomic import WriteFailure, atomic_write_text
from tools.freeze_reviewer.artifact import (
    STAMP_MARKER,
    FENCE_RE,
    ParsedArtifact,
    _operator_forced_md_prefix,
    artifact_digest,
    extract_existing_stamp,
    pre_stamp_canonical_bytes,
)
from tools.freeze_reviewer.serializer import dump_freeze_mapping, parse_freeze_mapping
from tools.freeze_reviewer.types import ReviewStamp, ReviewerSettings


def utc_now_z() -> str:
    """Return ISO-8601 UTC timestamp with trailing Z."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_stamp(
    parsed: ParsedArtifact,
    *,
    reviewer: ReviewerSettings,
    kit_version: str,
) -> ReviewStamp:
    """Build a review stamp payload for the current artifact."""
    return ReviewStamp(
        reviewed_at=utc_now_z(),
        verdict="pass",
        reviewer_mode=reviewer.mode,
        reviewer_model=reviewer.model,
        reviewer_provider=reviewer.provider,
        kit_version=kit_version,
        artifact_digest=artifact_digest(parsed),
    )


def stamp_is_idempotent_noop(parsed: ParsedArtifact, new_stamp: ReviewStamp) -> bool:
    """Return True when an existing pass stamp matches the recomputed digest."""
    existing = extract_existing_stamp(parsed)
    if not existing:
        return False
    if existing.get("verdict") != "pass":
        return False
    return existing.get("artifact_digest") == new_stamp.artifact_digest


def _insert_review_stamp(mapping: dict, stamp: ReviewStamp) -> dict:
    updated = dict(mapping)
    updated["review_stamp"] = stamp.to_mapping()
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
        stamp_yaml = dump_freeze_mapping({"review_stamp": stamp.to_mapping()})
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

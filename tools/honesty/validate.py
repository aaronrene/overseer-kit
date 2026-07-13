"""Ledger entry validation (§K9.7 / §K9.8)."""

from __future__ import annotations

from typing import Any

from tools.honesty.provenance import validate_provenance
from tools.honesty.types import ACTOR_ROLES, ENTRY_KINDS, EntryValidationError


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EntryValidationError(2, f"{field} must be an object")
    return value


def _require_non_empty_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EntryValidationError(2, f"{field} must be a non-empty string")
    return value


def validate_append_body(*, kind: str, body: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize an append body before hashing."""
    if kind not in ENTRY_KINDS:
        raise EntryValidationError(2, f"unknown entry kind: {kind}")

    if "entry_hash" in body or "prev_hash" in body:
        raise EntryValidationError(2, "client must not supply entry_hash or prev_hash")

    body_kind = body.get("kind")
    if body_kind is not None and body_kind != kind:
        raise EntryValidationError(2, "body kind must match --kind when present")

    merged = dict(body)
    merged["kind"] = kind

    version = merged.get("v", 1)
    if version != 1:
        raise EntryValidationError(2, "v must be integer 1")

    merged["v"] = 1

    if kind == "genesis":
        if "actor_role" in merged or "actor_session_id" in merged:
            raise EntryValidationError(2, "genesis must not carry actor fields")
        for key in ("assignment", "artifact_sha256", "passed", "evidence", "subject", "ruling", "bound_verdict_hash", "hook", "ok", "reason", "provenance"):
            if key in merged:
                raise EntryValidationError(2, f"genesis must not carry {key}")
        return merged

    actor_role = merged.get("actor_role")
    if actor_role not in ACTOR_ROLES:
        raise EntryValidationError(23 if kind == "verdict" else 2, "invalid or missing actor_role")

    actor_session = merged.get("actor_session_id")
    _require_non_empty_str(actor_session, "actor_session_id")

    if kind == "task_assigned":
        if actor_role != "overseer":
            raise EntryValidationError(23, "task_assigned requires actor_role=overseer")
        _require_mapping(merged.get("assignment"), "assignment")
    elif kind == "verdict":
        if actor_role != "verifier":
            raise EntryValidationError(23, "verdict requires actor_role=verifier")
        _require_non_empty_str(merged.get("artifact_sha256"), "artifact_sha256")
        passed = merged.get("passed")
        if not isinstance(passed, bool):
            raise EntryValidationError(2, "passed must be a boolean")
        evidence = _require_mapping(merged.get("evidence"), "evidence")
        reexecuted = evidence.get("reexecuted")
        if not isinstance(reexecuted, list) or not reexecuted:
            raise EntryValidationError(24, "evidence.reexecuted must be a non-empty list")
        if not all(isinstance(item, str) for item in reexecuted):
            raise EntryValidationError(2, "evidence.reexecuted entries must be strings")
    elif kind == "dispute_opened":
        _require_non_empty_str(merged.get("subject"), "subject")
    elif kind == "overseer_ruling":
        if actor_role != "overseer":
            raise EntryValidationError(23, "overseer_ruling requires actor_role=overseer")
        _require_non_empty_str(merged.get("ruling"), "ruling")
    elif kind == "approval_recorded":
        if actor_role != "owner":
            raise EntryValidationError(23, "approval_recorded requires actor_role=owner")
        _require_non_empty_str(merged.get("artifact_sha256"), "artifact_sha256")
        _require_non_empty_str(merged.get("bound_verdict_hash"), "bound_verdict_hash")
    elif kind == "board_advance":
        _require_non_empty_str(merged.get("artifact_sha256"), "artifact_sha256")
        _require_non_empty_str(merged.get("bound_verdict_hash"), "bound_verdict_hash")
    elif kind == "hook_check":
        hook = merged.get("hook")
        if hook not in {"board_done", "handoff", "register"}:
            raise EntryValidationError(2, "hook_check.hook must be board_done|handoff|register")
        ok = merged.get("ok")
        if not isinstance(ok, bool):
            raise EntryValidationError(2, "ok must be a boolean")
        reason = merged.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise EntryValidationError(2, "reason must be a string when present")

    if "provenance" in merged:
        merged["provenance"] = validate_provenance(merged["provenance"])

    return merged


def find_passing_verdict(
    entries: list[dict[str, Any]],
    *,
    artifact_sha256: str,
    bound_verdict_hash: str,
) -> bool:
    """Return True when a passing verifier verdict matches the bound hash."""
    for entry in entries:
        if entry.get("kind") != "verdict":
            continue
        if entry.get("actor_role") != "verifier":
            continue
        if entry.get("passed") is not True:
            continue
        if entry.get("artifact_sha256") != artifact_sha256:
            continue
        if entry.get("entry_hash") == bound_verdict_hash:
            return True
    return False

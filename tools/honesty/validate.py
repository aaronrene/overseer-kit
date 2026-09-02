"""Ledger entry validation (§K9.7 / §K9.8 / §PE.3–§PE.4)."""

from __future__ import annotations

import re
from typing import Any

from tools.honesty.provenance import validate_provenance
from tools.honesty.types import (
    ACTOR_ROLES,
    BV_VERDICTS,
    ENTRY_KINDS,
    ISR_VERDICTS,
    VERIFICATION_ARTIFACT_TYPES,
    EntryValidationError,
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EntryValidationError(2, f"{field} must be an object")
    return value


def _validate_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.match(value):
        raise EntryValidationError(2, f"{field} must be lowercase 64-char hex sha256")
    return value


def validate_verification_artifacts(artifacts: Any) -> list[dict[str, Any]]:
    """Validate ``verification_evidence.artifacts`` per §PE.4."""
    if not isinstance(artifacts, list) or not artifacts:
        raise EntryValidationError(24, "artifacts must be a non-empty list")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(artifacts):
        obj = _require_mapping(item, f"artifacts[{index}]")
        art_type = obj.get("type")
        if art_type not in VERIFICATION_ARTIFACT_TYPES:
            raise EntryValidationError(
                2,
                f"artifacts[{index}].type must be test_output|deploy_health|screenshot",
            )
        sha256 = _validate_sha256(obj.get("sha256"), f"artifacts[{index}].sha256")
        ref = obj.get("ref")
        if art_type in {"deploy_health", "screenshot"}:
            _require_non_empty_str(ref, f"artifacts[{index}].ref")
        elif ref is not None and not isinstance(ref, str):
            raise EntryValidationError(2, f"artifacts[{index}].ref must be a string when present")
        notes = obj.get("notes")
        if notes is not None and not isinstance(notes, str):
            raise EntryValidationError(2, f"artifacts[{index}].notes must be a string when present")
        entry: dict[str, Any] = {"type": art_type, "sha256": sha256}
        if ref is not None:
            entry["ref"] = ref
        if notes is not None:
            entry["notes"] = notes
        normalized.append(entry)
    return normalized


def find_matching_verification_evidence(
    entries: list[dict[str, Any]],
    *,
    phase_id: str,
    frozen_spec: str | None,
) -> dict[str, Any] | None:
    """Return the last matching pass entry for Mode B (§PE.6.1)."""
    matches: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("kind") != "verification_evidence":
            continue
        if entry.get("actor_role") != "verifier":
            continue
        if entry.get("bv_verdict") != "pass":
            continue
        if entry.get("phase_id") != phase_id:
            continue
        if frozen_spec is not None and entry.get("frozen_spec") != frozen_spec:
            continue
        matches.append(entry)
    return matches[-1] if matches else None


def find_matching_deploy_health(
    entries: list[dict[str, Any]],
    *,
    phase_id: str,
    frozen_spec: str | None,
) -> dict[str, Any] | None:
    """Return the last Mode C match: pass + ≥1 ``deploy_health`` artifact (§PD.3).

    Does not open network or treat ``ref`` as a URL.
    """
    matches: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("kind") != "verification_evidence":
            continue
        if entry.get("actor_role") != "verifier":
            continue
        if entry.get("bv_verdict") != "pass":
            continue
        if entry.get("phase_id") != phase_id:
            continue
        if frozen_spec is not None and entry.get("frozen_spec") != frozen_spec:
            continue
        artifacts = entry.get("artifacts")
        if not isinstance(artifacts, list):
            continue
        if not any(
            isinstance(item, dict) and item.get("type") == "deploy_health" for item in artifacts
        ):
            continue
        matches.append(entry)
    return matches[-1] if matches else None


def find_matching_independent_second_review(
    entries: list[dict[str, Any]],
    *,
    phase_id: str,
    frozen_spec: str | None,
    producer_session: str | None,
) -> dict[str, Any] | None:
    """Return the last matching ISR pass entry for Mode D (§ISR.5.3).

    Does not open a network connection, call a model, or read IDE session ids.
    """
    matches: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("kind") != "independent_second_review":
            continue
        if entry.get("actor_role") != "verifier":
            continue
        if entry.get("isr_verdict") != "pass":
            continue
        if entry.get("phase_id") != phase_id:
            continue
        if frozen_spec is not None and entry.get("frozen_spec") != frozen_spec:
            continue
        actor_session = entry.get("actor_session_id")
        producer_id = entry.get("producer_session_id")
        if not isinstance(actor_session, str) or not isinstance(producer_id, str):
            continue
        if actor_session == producer_id:
            continue
        if producer_session is not None:
            if producer_id != producer_session:
                continue
            if actor_session == producer_session:
                continue
        matches.append(entry)
    return matches[-1] if matches else None


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
        for key in (
            "assignment",
            "artifact_sha256",
            "passed",
            "evidence",
            "subject",
            "ruling",
            "bound_verdict_hash",
            "hook",
            "ok",
            "reason",
            "provenance",
            "phase_id",
            "frozen_spec",
            "round",
            "bv_verdict",
            "artifacts",
            "subject_sha256",
            "isr_verdict",
            "producer_session_id",
            "producer_agent_id",
            "verifier_agent_id",
            "bound_verification_evidence_hash",
        ):
            if key in merged:
                raise EntryValidationError(2, f"genesis must not carry {key}")
        return merged

    actor_role = merged.get("actor_role")
    if actor_role not in ACTOR_ROLES:
        raise EntryValidationError(
            23
            if kind in {"verdict", "verification_evidence", "independent_second_review"}
            else 2,
            "invalid or missing actor_role",
        )

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
    elif kind == "verification_evidence":
        if actor_role != "verifier":
            raise EntryValidationError(23, "verification_evidence requires actor_role=verifier")
        _require_non_empty_str(merged.get("phase_id"), "phase_id")
        _require_non_empty_str(merged.get("frozen_spec"), "frozen_spec")
        round_val = merged.get("round")
        if not isinstance(round_val, int) or round_val < 1:
            raise EntryValidationError(2, "round must be an integer >= 1")
        bv_verdict = merged.get("bv_verdict")
        if bv_verdict not in BV_VERDICTS:
            raise EntryValidationError(2, "bv_verdict must be pass|findings|blocked")
        merged["artifacts"] = validate_verification_artifacts(merged.get("artifacts"))
        subject_sha256 = merged.get("subject_sha256")
        if subject_sha256 is not None:
            _validate_sha256(subject_sha256, "subject_sha256")
        notes = merged.get("notes")
        if notes is not None and not isinstance(notes, str):
            raise EntryValidationError(2, "notes must be a string when present")
    elif kind == "independent_second_review":
        if actor_role != "verifier":
            raise EntryValidationError(
                23, "independent_second_review requires actor_role=verifier"
            )
        _require_non_empty_str(merged.get("phase_id"), "phase_id")
        _require_non_empty_str(merged.get("frozen_spec"), "frozen_spec")
        round_val = merged.get("round")
        if not isinstance(round_val, int) or round_val < 1:
            raise EntryValidationError(2, "round must be an integer >= 1")
        isr_verdict = merged.get("isr_verdict")
        if isr_verdict not in ISR_VERDICTS:
            raise EntryValidationError(2, "isr_verdict must be pass|findings|blocked")
        producer_session_id = _require_non_empty_str(
            merged.get("producer_session_id"), "producer_session_id"
        )
        if actor_session == producer_session_id:
            raise EntryValidationError(
                2, "actor_session_id must differ from producer_session_id"
            )
        producer_agent_id = merged.get("producer_agent_id")
        verifier_agent_id = merged.get("verifier_agent_id")
        if producer_agent_id is not None and not isinstance(producer_agent_id, str):
            raise EntryValidationError(2, "producer_agent_id must be a string when present")
        if verifier_agent_id is not None and not isinstance(verifier_agent_id, str):
            raise EntryValidationError(2, "verifier_agent_id must be a string when present")
        if (
            isinstance(producer_agent_id, str)
            and isinstance(verifier_agent_id, str)
            and producer_agent_id == verifier_agent_id
        ):
            raise EntryValidationError(
                2, "producer_agent_id must differ from verifier_agent_id when both present"
            )
        bound_hash = merged.get("bound_verification_evidence_hash")
        if bound_hash is not None:
            _require_non_empty_str(bound_hash, "bound_verification_evidence_hash")
        notes = merged.get("notes")
        if notes is not None and not isinstance(notes, str):
            raise EntryValidationError(2, "notes must be a string when present")

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

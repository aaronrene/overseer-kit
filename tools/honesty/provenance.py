"""Provenance envelope validation and signature verification (§P0.3 / §P0.4)."""

from __future__ import annotations

from typing import Any

from tools.honesty.ed25519_util import verify_ed25519_signature
from tools.honesty.muse_registry import MuseAgentKeyRegistry, NullMuseAgentKeyRegistry
from tools.honesty.types import EntryValidationError

PROVENANCE_KEYS = frozenset({"agent_id", "model_id", "human_ref", "sig", "pubkey"})
MUSE_REGIMES = frozenset({"muse+git-mirror", "muse-only"})
SIGNATURE_REQUIRED_KINDS = frozenset({"verdict", "approval_recorded"})


def _require_non_empty_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EntryValidationError(2, f"{field} must be a non-empty string")
    return value


def validate_provenance(raw: Any) -> dict[str, Any]:
    """Validate and normalize a ``provenance`` object (§P0.3)."""
    if not isinstance(raw, dict):
        raise EntryValidationError(2, "provenance must be an object")

    extra = set(raw) - PROVENANCE_KEYS
    if extra:
        raise EntryValidationError(2, f"unknown provenance keys: {sorted(extra)}")

    agent_id = _require_non_empty_str(raw.get("agent_id"), "provenance.agent_id")
    model_id = _require_non_empty_str(raw.get("model_id"), "provenance.model_id")

    human_ref = raw.get("human_ref")
    if human_ref is not None and not isinstance(human_ref, str):
        raise EntryValidationError(2, "provenance.human_ref must be a string or null")

    sig = raw.get("sig")
    pubkey = raw.get("pubkey")
    has_sig = sig is not None
    has_pubkey = pubkey is not None
    if has_sig != has_pubkey:
        raise EntryValidationError(2, "provenance.sig and provenance.pubkey must both be present or both absent")

    if has_sig:
        if not isinstance(sig, str) or not sig.startswith("ed25519:"):
            raise EntryValidationError(2, "provenance.sig must be ed25519:<base64>")
        if not isinstance(pubkey, str) or not pubkey.startswith("ed25519:"):
            raise EntryValidationError(2, "provenance.pubkey must be ed25519:<base64>")

    normalized: dict[str, Any] = {
        "agent_id": agent_id,
        "model_id": model_id,
    }
    if human_ref is not None:
        normalized["human_ref"] = human_ref
    if has_sig:
        normalized["sig"] = sig
        normalized["pubkey"] = pubkey
    return normalized


def resolve_verification_pubkey(
    provenance: dict[str, Any],
    *,
    regime: str,
    registry: MuseAgentKeyRegistry | None = None,
) -> str | None:
    """Resolve the pubkey token used to verify ``provenance.sig``."""
    embedded = provenance.get("pubkey")
    if isinstance(embedded, str) and embedded.startswith("ed25519:"):
        return embedded

    if regime in MUSE_REGIMES:
        human_ref = provenance.get("human_ref")
        agent_id = provenance.get("agent_id")
        if isinstance(human_ref, str) and isinstance(agent_id, str):
            lookup = registry if registry is not None else NullMuseAgentKeyRegistry()
            return lookup.resolve_pubkey(human_ref=human_ref, agent_id=agent_id)
    return None


def verify_entry_provenance(
    entry: dict[str, Any],
    *,
    regime: str,
    registry: MuseAgentKeyRegistry | None = None,
) -> int:
    """Verify optional provenance signature; return ``0`` or ``25``."""
    provenance = entry.get("provenance")
    if not isinstance(provenance, dict):
        return 0

    sig = provenance.get("sig")
    if not sig:
        return 0

    entry_hash = entry.get("entry_hash")
    if not isinstance(entry_hash, str):
        return 25

    pubkey = resolve_verification_pubkey(provenance, regime=regime, registry=registry)
    if pubkey is None:
        return 25

    if not verify_ed25519_signature(
        pubkey_token=pubkey,
        entry_hash_hex=entry_hash.lower(),
        sig_token=sig,
    ):
        return 25
    return 0


def signature_required_for_kind(*, require_agent_signature: bool, kind: str) -> bool:
    """Return True when a Muse-backed config mandates ``provenance.sig``."""
    return require_agent_signature and kind in SIGNATURE_REQUIRED_KINDS


def provenance_has_signature(body: dict[str, Any]) -> bool:
    """Return True when the append body carries a non-empty ``provenance.sig``."""
    provenance = body.get("provenance")
    if not isinstance(provenance, dict):
        return False
    sig = provenance.get("sig")
    return isinstance(sig, str) and bool(sig.strip())

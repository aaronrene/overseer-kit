"""Canonical JSON and entry hashing (§K9.7)."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize ``value`` as canonical JSON for hashing."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _hash_payload(body: dict[str, Any]) -> dict[str, Any]:
    """Build the canonical-hash payload, excluding ``entry_hash`` and ``provenance.sig``."""
    payload = {key: val for key, val in body.items() if key != "entry_hash"}
    provenance = payload.get("provenance")
    if isinstance(provenance, dict) and "sig" in provenance:
        stripped = {key: val for key, val in provenance.items() if key != "sig"}
        payload = {**payload, "provenance": stripped}
    return payload


def compute_entry_hash(body: dict[str, Any]) -> str:
    """Compute lowercase hex SHA-256 of canonical JSON without ``entry_hash`` or ``provenance.sig``."""
    digest = hashlib.sha256(canonical_json(_hash_payload(body)).encode("utf-8")).hexdigest()
    return digest.lower()

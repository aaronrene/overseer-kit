"""Canonical JSON and entry hashing (§K9.7)."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize ``value`` as canonical JSON for hashing."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def compute_entry_hash(body: dict[str, Any]) -> str:
    """Compute lowercase hex SHA-256 of canonical JSON without ``entry_hash``."""
    payload = {key: val for key, val in body.items() if key != "entry_hash"}
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return digest.lower()

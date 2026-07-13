"""Ledger genesis constant and entry factory (§K9.7)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from tools.honesty.canonical import compute_entry_hash

_GENESIS_SEED = b"overseer-kit-honesty-ledger-v1"
GENESIS_PREV = hashlib.sha256(_GENESIS_SEED).hexdigest().lower()


def utc_now_z() -> str:
    """Return ISO-8601 UTC timestamp with ``Z`` suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_genesis_entry(ts: str | None = None) -> dict[str, Any]:
    """Construct a genesis ledger entry with server-filled hashes."""
    timestamp = ts or utc_now_z()
    body: dict[str, Any] = {
        "v": 1,
        "ts": timestamp,
        "kind": "genesis",
        "prev_hash": GENESIS_PREV,
    }
    body["entry_hash"] = compute_entry_hash(body)
    return body

"""Viewer Bearer credential helpers (§HGD.6.1)."""

from __future__ import annotations

import secrets

# ≥ 128 bits entropy (16 bytes → 32 hex chars).
_VIEWER_TOKEN_BYTES = 16


def generate_viewer_token() -> str:
    """Return a cryptographically secure viewer Bearer credential."""
    return secrets.token_hex(_VIEWER_TOKEN_BYTES)


def constant_time_equal(a: str, b: str) -> bool:
    """Compare two strings in constant time."""
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))

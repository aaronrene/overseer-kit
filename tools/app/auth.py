"""Session credential and CSRF generation for the local app server (§Q0.6)."""

from __future__ import annotations

import secrets


def generate_session_credential() -> str:
    """Return a cryptographically secure token with at least 128 bits of entropy."""
    return secrets.token_hex(16)


def generate_csrf_token() -> str:
    """Return a CSRF token with at least 128 bits of entropy."""
    return secrets.token_hex(16)


def constant_time_equal(a: str, b: str) -> bool:
    """Compare two strings in constant time."""
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))

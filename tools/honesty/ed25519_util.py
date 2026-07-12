"""Ed25519 helpers for provenance signatures (§P0.4).

The kit verifies signatures only; it never loads or stores private keys.
"""

from __future__ import annotations

import base64
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ED25519_PREFIX = "ed25519:"


class Ed25519FormatError(ValueError):
    """Raised when an ``ed25519:`` token is malformed."""


def encode_ed25519_token(raw: bytes) -> str:
    """Encode raw bytes as ``ed25519:<base64>``."""
    return f"{ED25519_PREFIX}{base64.b64encode(raw).decode('ascii')}"


def decode_ed25519_token(token: Any, *, field: str) -> bytes:
    """Decode ``ed25519:<base64>`` to raw bytes; fail closed on malformed input."""
    if not isinstance(token, str) or not token.startswith(ED25519_PREFIX):
        raise Ed25519FormatError(f"{field} must be ed25519:<base64>")
    payload = token[len(ED25519_PREFIX) :]
    if not payload:
        raise Ed25519FormatError(f"{field} must be ed25519:<base64>")
    try:
        return base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise Ed25519FormatError(f"{field} must be valid base64") from exc


def verify_ed25519_signature(*, pubkey_token: str, entry_hash_hex: str, sig_token: str) -> bool:
    """Return True when ``sig_token`` is a valid Ed25519 signature over ``entry_hash_hex``."""
    try:
        pubkey_bytes = decode_ed25519_token(pubkey_token, field="provenance.pubkey")
        sig_bytes = decode_ed25519_token(sig_token, field="provenance.sig")
        public_key = Ed25519PublicKey.from_public_bytes(pubkey_bytes)
        public_key.verify(sig_bytes, entry_hash_hex.encode("utf-8"))
    except (Ed25519FormatError, InvalidSignature, ValueError):
        return False
    return True

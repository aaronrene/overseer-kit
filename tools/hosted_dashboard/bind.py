"""Bind + port policy for hosted-dashboard preview (§HGD.6.4, §HGD.10.1)."""

from __future__ import annotations

import ipaddress
import socket

DEFAULT_PORT = 8766
LOOPBACK_LITERALS = frozenset({"127.0.0.1", "localhost", "::1"})


def normalize_bind_address(bind: str) -> str:
    """Normalize bind literal for ``HTTPServer``."""
    text = bind.strip()
    if text == "localhost":
        return "127.0.0.1"
    return text


def is_loopback_bind(bind: str) -> bool:
    """Return whether ``bind`` is a loopback literal."""
    return bind.strip() in LOOPBACK_LITERALS


def validate_bind_address(bind: str, *, allow_non_loopback: bool) -> str | None:
    """Return normalized bind address, or ``None`` when refused.

    Non-loopback binds require ``allow_non_loopback=True`` (config + auth/TLS rules).
    """
    text = bind.strip()
    if text in LOOPBACK_LITERALS:
        return normalize_bind_address(text)
    if not allow_non_loopback:
        return None
    # Refuse wildcard-ish and empty; allow concrete operator hosts when opted in.
    if not text or text in {"*", ""}:
        return None
    return text


def is_loopback_peer(host: str) -> bool:
    """Return whether ``host`` is a loopback peer address."""
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def port_is_available(bind: str, port: int) -> bool:
    """Return whether ``port`` can be bound on ``bind``."""
    family = socket.AF_INET6 if bind == "::1" else socket.AF_INET
    probe_host = bind if bind != "127.0.0.1" else "127.0.0.1"
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((probe_host, port))
        except OSError:
            return False
    return True

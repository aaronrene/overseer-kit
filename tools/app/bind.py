"""Loopback bind policy for ``overseer app`` (§Q0.5)."""

from __future__ import annotations

import ipaddress
import socket


DEFAULT_PORT = 8765
ALLOWED_BIND_LITERALS = frozenset({"127.0.0.1", "localhost", "::1"})


def normalize_bind_address(bind: str) -> str:
    """Normalize an allowed bind literal to the address passed to ``HTTPServer``."""
    text = bind.strip()
    if text == "localhost":
        return "127.0.0.1"
    return text


def validate_bind_address(bind: str) -> str | None:
    """Return normalized bind address, or ``None`` when the literal is refused."""
    text = bind.strip()
    if text not in ALLOWED_BIND_LITERALS:
        return None
    return normalize_bind_address(text)


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

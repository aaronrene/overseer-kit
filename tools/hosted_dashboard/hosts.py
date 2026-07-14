"""Upstream host allowlist (§HGD.6.6)."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

DEFAULT_ALLOWED_HOSTS = frozenset(
    {
        "api.github.com",
        "raw.githubusercontent.com",
    }
)

# Optional muse deepen hosts must be explicitly configured (finite list, no wildcards).
_HOSTNAME_RE = re.compile(r"^(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}$|^[A-Za-z0-9-]+$")


def _is_literal_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _is_blocked_special(host: str) -> bool:
    """Refuse link-local / metadata / loopback IP literals always."""
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        lowered = host.lower()
        return lowered in {"localhost", "metadata.google.internal"}
    return bool(
        addr.is_loopback
        or addr.is_link_local
        or addr.is_private
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def host_allowed(host: str, *, extra_allowed: frozenset[str] | None = None) -> bool:
    """Return whether ``host`` may be contacted as an upstream.

    Literal IPs and link-local/metadata addresses are always refused.
    """
    if not host or not isinstance(host, str):
        return False
    hostname = host.strip().lower().split("%", 1)[0]
    if not hostname:
        return False
    if _is_literal_ip(hostname):
        return False
    if _is_blocked_special(hostname):
        return False
    allowed = DEFAULT_ALLOWED_HOSTS | (extra_allowed or frozenset())
    return hostname in allowed


def url_host_allowed(url: str, *, extra_allowed: frozenset[str] | None = None) -> bool:
    """Parse ``url`` and check its hostname against the allowlist."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in {"https", "http"}:
        return False
    host = parsed.hostname
    if host is None:
        return False
    return host_allowed(host, extra_allowed=extra_allowed)


def validate_extra_hosts(hosts: list[str]) -> frozenset[str]:
    """Validate optional muse deepen hostnames (finite, no wildcards, no IPs)."""
    out: set[str] = set()
    for raw in hosts:
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError("empty muse host")
        host = raw.strip().lower()
        if "*" in host or host.startswith("."):
            raise ValueError(f"wildcard muse host refused: {raw!r}")
        if _is_literal_ip(host) or _is_blocked_special(host):
            raise ValueError(f"disallowed muse host: {raw!r}")
        if not _HOSTNAME_RE.match(host):
            raise ValueError(f"invalid muse host: {raw!r}")
        out.add(host)
    return frozenset(out)

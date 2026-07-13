"""CORS policy for the local app server (§Q0.5)."""

from __future__ import annotations


def allowed_origins(port: int) -> frozenset[str]:
    """Return the frozen allowlist of browser origins."""
    return frozenset(
        {
            f"http://127.0.0.1:{port}",
            f"http://localhost:{port}",
            f"http://[::1]:{port}",
        }
    )


def origin_allowed(origin: str | None, port: int) -> bool:
    """Return whether ``origin`` is permitted for this server instance."""
    if not origin:
        return True
    return origin in allowed_origins(port)

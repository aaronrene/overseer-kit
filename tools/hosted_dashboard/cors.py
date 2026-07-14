"""CORS allowlist for hosted dashboard (§HGD.6.3)."""

from __future__ import annotations


def origin_allowed(origin: str | None, cors_origins: tuple[str, ...]) -> bool:
    """Return whether Origin is allowed.

    Missing Origin (same-origin / non-browser) is allowed.
    When cors_origins is empty, any explicit Origin is denied (fail closed for
    cross-origin) except missing Origin.
    """
    if origin is None or origin == "":
        return True
    return origin in cors_origins

"""Closed source-id vocabulary (§HGD.4.1)."""

from __future__ import annotations

SOURCE_IDS = frozenset(
    {
        "github_contents",
        "github_meta",
        "github_checks_advisory",
        "musehub_read",
    }
)
BASELINE_SOURCE_IDS = frozenset({"github_contents", "github_meta"})
OPTIONAL_SOURCE_IDS = frozenset({"github_checks_advisory", "musehub_read"})


def is_known_source_id(source_id: str) -> bool:
    """Return whether ``source_id`` is in the closed Auto v1 vocabulary."""
    return source_id in SOURCE_IDS

"""Owner/repo/path validators and allowlist helpers (§HGD.4.2, §HGD.5.3)."""

from __future__ import annotations

import re

OWNER_REPO_SEGMENT_RE = re.compile(r"^[A-Za-z0-9._-]+$")
ALLOWLIST_ENTRY_RE = re.compile(r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)?$")

DEFAULT_ORG_ENUMERATION_CAP = 100
DEFAULT_ROADMAP_PATH = "docs/ROADMAP.md"
DEFAULT_HANDOVER_PATH = "docs/OVERSEER-HANDOVER.md"
MARKER_PATH = ".overseer/config.yaml"


def valid_owner_repo_segment(value: str) -> bool:
    """Return whether ``value`` matches the frozen owner/repo segment pattern."""
    return bool(value) and bool(OWNER_REPO_SEGMENT_RE.match(value))


def parse_allowlist_entry(entry: str) -> tuple[str, str | None]:
    """Parse an allowlist entry into ``(owner, repo_or_None)``.

    Raises ``ValueError`` when the entry does not match the frozen shape.
    """
    if not isinstance(entry, str) or not entry.strip():
        raise ValueError("empty allowlist entry")
    text = entry.strip()
    if not ALLOWLIST_ENTRY_RE.match(text):
        raise ValueError(f"invalid allowlist entry: {entry!r}")
    if "/" in text:
        owner, repo = text.split("/", 1)
        return owner, repo
    return text, None


def validate_allowlist(entries: list[str]) -> list[tuple[str, str | None]]:
    """Validate and return normalized allowlist pairs."""
    return [parse_allowlist_entry(e) for e in entries]


def unknown_query_keys(query: dict[str, list[str]], *, allowed: frozenset[str] = frozenset()) -> list[str]:
    """Return query keys not in ``allowed`` (empty allowed → any key is unknown)."""
    return sorted(k for k in query if k not in allowed)

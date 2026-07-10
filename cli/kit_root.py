"""Locate the kit installation root and carried version."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def kit_root() -> Path:
    """Return the absolute path to the overseer-kit root (parent of ``cli/``)."""
    return Path(__file__).resolve().parent.parent


def kit_version() -> str:
    """Read the semver carried by this CLI from ``VERSION``."""
    version_path = kit_root() / "VERSION"
    return version_path.read_text(encoding="utf-8").strip()

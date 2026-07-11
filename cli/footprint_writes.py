"""Footprint file writes with regime-specific modes (§K7.3.1 executable script)."""

from __future__ import annotations

import os
from pathlib import Path

from cli.atomic import WriteFailure, atomic_write_bytes
from cli.footprint import EXECUTABLE_FOOTPRINT_DESTINATIONS

FOOTPRINT_EXECUTABLE_MODE = 0o755


def write_footprint_bytes(path: Path, data: bytes, *, destination: str) -> None:
    """Atomically write one footprint file; set mode ``0755`` for executable destinations."""
    atomic_write_bytes(path, data)
    if destination in EXECUTABLE_FOOTPRINT_DESTINATIONS:
        try:
            path.chmod(FOOTPRINT_EXECUTABLE_MODE)
        except OSError as exc:
            raise WriteFailure(path, exc) from exc

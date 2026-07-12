"""Artifact digest helpers (§K9.8)."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file_bytes(path: Path) -> str:
    """Return lowercase hex SHA-256 of raw file bytes."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest.lower()

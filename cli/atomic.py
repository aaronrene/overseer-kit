"""Atomic per-file writes per §K4.8."""

from __future__ import annotations

import os
from pathlib import Path


class WriteFailure(Exception):
    """Raised when an atomic write fails."""

    def __init__(self, path: Path, cause: OSError) -> None:
        self.path = path
        self.cause = cause
        super().__init__(f"write failed for {path}: {cause}")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write ``data`` atomically via temp file + ``os.replace``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.overseer.tmp")
    try:
        tmp_path.write_bytes(data)
        os.replace(tmp_path, path)
    except OSError as exc:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise WriteFailure(path, exc) from exc


def atomic_write_text(path: Path, text: str) -> None:
    """Write UTF-8 text atomically."""
    atomic_write_bytes(path, text.encode("utf-8"))

"""Footprint digest computation per §K4.7."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FootprintRecord:
    """Per-file digest record for manifest and aggregate hash."""

    path: str
    sha256_hex: str


def canonical_bytes(data: bytes) -> bytes:
    """Normalize line endings to LF without altering trailing newline count."""
    text = data.decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Return lowercase hex sha256 of canonical bytes."""
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def sha256_hex_raw(data: bytes) -> str:
    """Return lowercase hex sha256 of raw bytes (for manifest aggregate)."""
    return hashlib.sha256(data).hexdigest()


def build_manifest_lines(records: list[FootprintRecord]) -> str:
    """Build the sorted sha256sum-style manifest string."""
    sorted_records = sorted(records, key=lambda r: r.path)
    lines = [f"{rec.sha256_hex}  {rec.path}\n" for rec in sorted_records]
    return "".join(lines)


def compute_footprint_digest(records: list[FootprintRecord]) -> str:
    """Compute aggregate ``sha256:<hex>`` digest over sorted manifest lines."""
    manifest = build_manifest_lines(records)
    digest_hex = sha256_hex_raw(manifest.encode("utf-8"))
    return f"sha256:{digest_hex}"


def records_from_bytes(path: str, content: bytes) -> FootprintRecord:
    """Create a per-file record from raw file bytes."""
    return FootprintRecord(path=path, sha256_hex=sha256_hex(content))

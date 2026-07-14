"""Checksum helpers for release artifacts (§QR.7.3)."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Return lowercase hex SHA-256 of ``path`` using single-pass streaming."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def format_sha256sums_line(sha256: str, filename: str) -> str:
    """Return one ``SHA256SUMS.txt`` line (``sha256  filename``)."""
    return f"{sha256.lower()}  {filename}"


def write_sha256sums(
    destination: Path,
    entries: list[tuple[str, str]],
) -> str:
    """Write ``SHA256SUMS.txt`` content and return the text written.

    Parameters
    ----------
    destination:
        Output path (typically ``SHA256SUMS.txt``).
    entries:
        List of ``(sha256, filename)`` pairs in publish order.
    """
    lines = [format_sha256sums_line(sha, name) for sha, name in entries]
    text = "\n".join(lines) + ("\n" if lines else "")
    destination.write_text(text, encoding="utf-8")
    return text


def parse_sha256sums(text: str) -> dict[str, str]:
    """Parse ``sha256  filename`` lines into ``{filename: sha256}``.

    Filenames may contain spaces; the separator is two spaces after the digest
    (GNU ``sha256sum`` style), with a fallback to the first whitespace split
    when no double-space is present.
    """
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "  " in stripped:
            sha256, filename = stripped.split("  ", 1)
        else:
            parts = stripped.split(None, 1)
            if len(parts) < 2:
                raise ValueError(f"invalid SHA256SUMS line: {line!r}")
            sha256, filename = parts[0], parts[1]
        result[filename.strip()] = sha256.strip().lower()
    return result

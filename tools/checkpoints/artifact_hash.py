"""Parse ``ARTIFACT_SHA256`` from verify script stdout (§K9.5)."""

from __future__ import annotations

import re

_SHA_LINE = re.compile(r"^ARTIFACT_SHA256=([0-9a-fA-F]+)$")


def parse_artifact_sha256(stdout: bytes) -> str | None:
    """Decode stdout, strip trailing newlines, parse last line for artifact hash."""
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None
    stripped = text.rstrip("\n\r")
    if not stripped:
        return None
    if "\n" in stripped:
        line = stripped.rsplit("\n", 1)[-1]
    else:
        line = stripped
    match = _SHA_LINE.match(line)
    if not match:
        return None
    return match.group(1).lower()

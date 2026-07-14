"""Publish allowlist for GitHub Release assets (§QR.4.5)."""

from __future__ import annotations

import re

from tools.desktop_release.constants import (
    ALLOWED_INSTALLER_SUFFIXES,
    ALLOWED_SIDECAR_SUFFIXES,
    MANIFEST_FILENAME_TEMPLATE,
    SHA256SUMS_FILENAME,
)

_UNSIGNED_MARKERS = ("unsigned", "-unsigned", "_unsigned")


class AllowlistError(ValueError):
    """Raised when a filename is not on the Auto v1 publish allowlist."""


_MANIFEST_RE = re.compile(r"^overseer-kit-desktop-.+-manifest\.json$")


def is_allowed_release_asset(filename: str, *, version: str | None = None) -> bool:
    """Return True if ``filename`` may attach to a GitHub Release (§QR.4.5)."""
    name = filename.strip()
    if not name or "/" in name or "\\" in name:
        return False
    lower = name.lower()
    for marker in _UNSIGNED_MARKERS:
        if marker in lower:
            return False
    if name == SHA256SUMS_FILENAME:
        return True
    if version is not None:
        expected = MANIFEST_FILENAME_TEMPLATE.format(version=version.strip())
        if name == expected:
            return True
    elif _MANIFEST_RE.match(name):
        return True
    for suffix in ALLOWED_SIDECAR_SUFFIXES:
        if name.endswith(suffix):
            return True
    for suffix in ALLOWED_INSTALLER_SUFFIXES:
        if name.endswith(suffix):
            return True
    return False


def refuse_disallowed_asset(filename: str, *, version: str | None = None) -> None:
    """Raise :class:`AllowlistError` when filename is not allowlisted."""
    if not is_allowed_release_asset(filename, version=version):
        raise AllowlistError(f"release asset not on allowlist: {filename!r}")

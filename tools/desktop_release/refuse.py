"""Secret-pattern refuse helpers (§QR.6.3)."""

from __future__ import annotations

import re
from pathlib import Path

from tools.desktop_release.constants import PRIVATE_KEY_BASENAME_MARKERS, PUBLIC_KEY_ALLOWED_SUFFIXES

# Private-key PEM headers (workflow / tree lint).
_PEM_PRIVATE_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
)
# Hard-coded password assignments in YAML (crude but fail-closed for literals).
_HARDCODED_PASSWORD_RE = re.compile(
    r"(?i)(password|passwd|secret)\s*[:=]\s*['\"][^'\"]{4,}['\"]",
)
# PFX / PKCS12 magic often appears as base64 of 0x30 0x82… — flag obvious literals.
_PFX_MAGIC_RE = re.compile(r"(?i)MII[A-Za-z0-9+/]{40,}={0,2}")


class RefuseError(ValueError):
    """Raised when secret-like material is refused."""


def scan_text_for_secret_patterns(text: str) -> list[str]:
    """Return list of matched secret-pattern labels (empty = clean)."""
    hits: list[str] = []
    if _PEM_PRIVATE_RE.search(text):
        hits.append("pem_private_key")
    if _HARDCODED_PASSWORD_RE.search(text):
        hits.append("hardcoded_password")
    # Avoid flagging `${{ secrets.NAME }}` — only large base64-looking blobs.
    for match in _PFX_MAGIC_RE.finditer(text):
        snippet = match.group(0)
        if "secrets." in text[max(0, match.start() - 40) : match.start()]:
            continue
        if len(snippet) >= 64:
            hits.append("pfx_like_blob")
            break
    return hits


def refuse_secret_write_to_repo(path: Path, content: bytes | str) -> None:
    """Refuse writing secret-like content into a repo path.

    Used by tests and helpers — not a runtime daemon. Raises :class:`RefuseError`
    when content matches private-key / password / PFX patterns.
    """
    text = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else content
    hits = scan_text_for_secret_patterns(text)
    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix in {".p12", ".pfx"} or name.endswith(".p12") or name.endswith(".pfx"):
        hits.append("cert_file_extension")
    if hits:
        raise RefuseError(f"refuse writing secrets to {path}: {', '.join(hits)}")


def refuse_private_key_under_desktop_keys(path: Path) -> None:
    """Refuse private-key style filenames under ``desktop/keys/``.

    Public material (``.pub``, ``.asc``, ``.minisign.pub``, ``README.md``) is allowed.
    """
    parts = Path(path).as_posix().replace("\\", "/").split("/")
    try:
        desktop_idx = parts.index("desktop")
        keys_idx = parts.index("keys", desktop_idx + 1)
    except ValueError:
        return
    if keys_idx != desktop_idx + 1:
        return
    if keys_idx + 1 >= len(parts):
        return
    basename = parts[-1]
    if basename in {"README.md", ".gitkeep"}:
        return
    lower = basename.lower()
    if any(lower.endswith(suf) for suf in PUBLIC_KEY_ALLOWED_SUFFIXES):
        return
    if any(marker in lower for marker in PRIVATE_KEY_BASENAME_MARKERS):
        raise RefuseError(f"private key filename refused under desktop/keys/: {basename}")
    if lower.endswith((".pem", ".p12", ".pfx", ".key")):
        raise RefuseError(f"private key filename refused under desktop/keys/: {basename}")

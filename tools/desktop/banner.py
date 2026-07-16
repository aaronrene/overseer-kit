"""Parse ``ok app`` startup banner lines for the desktop launcher."""

from __future__ import annotations

import re
from dataclasses import dataclass

from tools.desktop.constants import (
    CSRF_PREFIX,
    LISTENING_BANNER,
    SESSION_PREFIX,
    URL_PREFIX,
)

_URL_RE = re.compile(r"^url:\s*(\S+)\s*$")
_SESSION_RE = re.compile(r"^session_credential:\s*(\S+)\s*$")
_CSRF_RE = re.compile(r"^csrf_token:\s*(\S+)\s*$")


@dataclass(frozen=True)
class StartupBanner:
    """Credentials and URL emitted once on ``ok app`` stderr."""

    url: str
    session_credential: str
    csrf_token: str

    @property
    def origin(self) -> str:
        """Return the loopback origin for CORS checks in packaging tests."""
        from urllib.parse import urlparse

        parsed = urlparse(self.url)
        return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"


def parse_startup_banner_line(line: str) -> tuple[str, str] | None:
    """Parse a single stderr line; return ``(field, value)`` or ``None``."""
    text = line.rstrip("\n")
    if text == LISTENING_BANNER:
        return ("listening", text)
    for pattern, field in (
        (_URL_RE, "url"),
        (_SESSION_RE, "session_credential"),
        (_CSRF_RE, "csrf_token"),
    ):
        match = pattern.match(text)
        if match:
            return (field, match.group(1))
    return None


def parse_startup_stderr(lines: list[str]) -> StartupBanner | None:
    """Collect banner fields from stderr lines; return ``None`` when incomplete."""
    url: str | None = None
    session: str | None = None
    csrf: str | None = None
    for line in lines:
        parsed = parse_startup_banner_line(line)
        if parsed is None:
            continue
        field, value = parsed
        if field == "url":
            url = value
        elif field == "session_credential":
            session = value
        elif field == "csrf_token":
            csrf = value
    if url and session and csrf:
        return StartupBanner(url=url, session_credential=session, csrf_token=csrf)
    return None

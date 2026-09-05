"""Read-only CURRENT NEXT paste extraction (§ONS / §NXP)."""

from __future__ import annotations

from tools.print_next.extract import (
    CURRENT_NEXT_HEADING,
    PROVENANCE_LINE_TEMPLATE,
    PROVENANCE_SEPARATOR,
    CurrentNextError,
    CurrentNextResult,
    absolute_repo_root,
    extract_current_next,
    format_current_next,
    format_provenance_line,
    read_at_now,
    set_read_at_clock,
    utc_read_at,
)

__all__ = [
    "CURRENT_NEXT_HEADING",
    "PROVENANCE_LINE_TEMPLATE",
    "PROVENANCE_SEPARATOR",
    "CurrentNextError",
    "CurrentNextResult",
    "absolute_repo_root",
    "extract_current_next",
    "format_current_next",
    "format_provenance_line",
    "read_at_now",
    "set_read_at_clock",
    "utc_read_at",
]

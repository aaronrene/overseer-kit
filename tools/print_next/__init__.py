"""Read-only CURRENT NEXT paste extraction (§ONS)."""

from __future__ import annotations

from tools.print_next.extract import (
    CURRENT_NEXT_HEADING,
    CurrentNextError,
    CurrentNextResult,
    extract_current_next,
    format_current_next,
)

__all__ = [
    "CURRENT_NEXT_HEADING",
    "CurrentNextError",
    "CurrentNextResult",
    "extract_current_next",
    "format_current_next",
]

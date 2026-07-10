"""Sanitize CLI output to avoid absolute machine paths (§K4.9)."""

from __future__ import annotations

from pathlib import Path


def sanitize_text(text: str, repo_root: Path) -> str:
    """Replace the resolved repo root prefix with ``.`` in free-form text."""
    root = str(repo_root.resolve())
    return text.replace(root, ".")


def format_config_error(exc, repo_root: Path) -> str:
    """Format a config error without leaking absolute paths."""
    return exc.message

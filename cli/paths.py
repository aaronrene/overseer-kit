"""Repo-root resolution and path confinement (§K4.1 / §K4.9)."""

from __future__ import annotations

import os
from pathlib import Path


class PathEscapeError(Exception):
    """Raised when a path would escape the resolved repo root."""


def resolve_repo_root(
    *,
    cwd: Path,
    repo_arg: str | None,
    command: str,
) -> Path:
    """Resolve and absolutize the consumer repo root per §K4.1."""
    if repo_arg is not None:
        return Path(repo_arg).expanduser().resolve()

    if command == "init":
        return cwd.resolve()

    current = cwd.resolve()
    for directory in (current, *current.parents):
        if (directory / ".overseer").is_dir():
            return directory
    return current


def resolve_config_path(repo_root: Path, config_arg: str | None) -> Path:
    """Resolve the config file path; default ``<repo>/.overseer/config.yaml``."""
    if config_arg is not None:
        path = Path(config_arg).expanduser()
        if not path.is_absolute():
            path = repo_root / path
        return path.resolve()
    return (repo_root / ".overseer" / "config.yaml").resolve()


def repo_relative(repo_root: Path, path: Path) -> str:
    """Return a POSIX repo-relative path, or ``.`` for the root."""
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(repo_root.resolve())
    except ValueError:
        raise PathEscapeError(f"path escapes repo root: {path}") from None
    text = rel.as_posix()
    return text if text else "."


def confine_path(repo_root: Path, user_path: str) -> Path:
    """Resolve ``user_path`` under ``repo_root``; reject traversal escapes."""
    root = repo_root.resolve()
    candidate = Path(user_path).expanduser()
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise PathEscapeError(f"path escapes repo root: {user_path}") from None
    return resolved


def is_within_repo(repo_root: Path, path: Path) -> bool:
    """Return True if ``path`` is inside ``repo_root``."""
    try:
        path.resolve().relative_to(repo_root.resolve())
        return True
    except ValueError:
        return False

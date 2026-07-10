"""Overseer Kit VCS adapters — config loading and backend factory."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from adapters.errors import ConfigError
from adapters.factory import create_adapter
from adapters.runner import CommandRunner

__all__ = [
    "CommandRunner",
    "ConfigError",
    "create_adapter",
    "load_config",
]

SUPPORTED_CONFIG_VERSION = 1
SUPPORTED_REGIMES = frozenset({"muse+git-mirror", "muse-only", "git-only"})


def load_adapter(
    repo_root: Path,
    config_path: Path | None = None,
    runner: CommandRunner | None = None,
):
    """Load config and return the regime-appropriate VCS adapter.

    Fail-closed: missing/unparseable config, unknown version, or unknown regime
    raises ``ConfigError``.
    """
    path = config_path or (repo_root / ".overseer" / "config.yaml")
    config = load_config(path)
    return create_adapter(config, repo_root.resolve(), runner=runner)

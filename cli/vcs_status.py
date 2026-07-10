"""Read-only VCS status via adapter (§K4.0)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import OverseerConfig
from adapters.errors import ReadError
from adapters.factory import create_adapter
from adapters.runner import CommandRunner
from adapters.types import StatusResult


def read_vcs_status(
    config: OverseerConfig,
    repo_root: Path,
    runner: CommandRunner,
) -> StatusResult | ReadError:
    """Call only ``adapter.status()`` for CLI commands."""
    adapter = create_adapter(config, repo_root, runner=runner)
    return adapter.status()


def vcs_report(result: StatusResult, config: OverseerConfig) -> dict:
    """Build the frozen ``vcs`` object for status output."""
    return {
        "regime": result.regime,
        "canonical": config.vcs.canonical,
        "branch": result.branch,
        "dirty": result.dirty,
        "notes": list(result.notes),
    }

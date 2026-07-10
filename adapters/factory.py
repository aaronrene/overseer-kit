"""Factory for regime-specific VCS adapters."""

from __future__ import annotations

from pathlib import Path

from adapters.base import VcsAdapter
from adapters.config import OverseerConfig
from adapters.errors import ConfigError
from adapters.runner import CommandRunner


def create_adapter(
    config: OverseerConfig,
    repo_root: Path,
    runner: CommandRunner | None = None,
) -> VcsAdapter:
    """Instantiate the adapter for ``config.vcs.regime``."""
    regime = config.vcs.regime
    if regime == "git-only":
        from adapters.git_only.adapter import GitOnlyAdapter

        return GitOnlyAdapter(config, repo_root, runner=runner)
    if regime == "muse-only":
        from adapters.muse_only.adapter import MuseOnlyAdapter

        return MuseOnlyAdapter(config, repo_root, runner=runner)
    if regime == "muse+git-mirror":
        from adapters.muse_git_mirror.adapter import MuseGitMirrorAdapter

        return MuseGitMirrorAdapter(config, repo_root, runner=runner)
    raise ConfigError(f"unsupported vcs.regime {regime!r}")

"""Module and hook gates for L2 commands (§K9.2 / §K9.8)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import HonestyConfig, OverseerConfig
from cli.paths import confine_path


ROLES_FILE_V1_WARNING = (
    "honesty.roles_file is set but v1 does not load roster content for enforcement "
    "(role gates remain enum-only)"
)


def honesty_module_disabled(config: OverseerConfig) -> bool:
    """Return True when the L2 operational gate is off."""
    return not config.honesty.enabled


def check_roles_file(
    honesty: HonestyConfig,
    repo_root: Path,
) -> tuple[int | None, str | None]:
    """Apply roles_file v1 path rule; return (exit_code, warning)."""
    if honesty.roles_file is None:
        return None, None
    try:
        roles_path = confine_path(repo_root, honesty.roles_file)
    except Exception:
        return 4, None
    if not roles_path.is_file():
        return 4, None
    return None, ROLES_FILE_V1_WARNING


def hook_enabled(config: OverseerConfig, hook: str) -> bool:
    """Return True when ``hook`` is in the effective require_verdict_on set."""
    return hook in config.honesty.require_verdict_on

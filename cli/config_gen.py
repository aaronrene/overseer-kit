"""Default config generation for ``overseer init``."""

from __future__ import annotations

from pathlib import Path

import yaml

from adapters.config import SUPPORTED_CONFIG_VERSION, OverseerConfig, load_config
from adapters.errors import ConfigError


def detect_regime(repo_root: Path) -> str | None:
    """Advisory regime detection from repo markers."""
    has_git = (repo_root / ".git").exists()
    has_muse = (repo_root / ".muse").is_dir()
    has_bridge = (repo_root / ".muse" / "git-bridge.toml").is_file()
    if has_bridge:
        return "muse+git-mirror"
    if has_muse:
        return "muse-only"
    if has_git:
        return "git-only"
    return None


def default_config_dict(
    *,
    regime: str,
    repo_name: str,
    docs_dir: str,
) -> dict:
    """Build a default config mapping for the given regime."""
    docs_dir = docs_dir.strip("/") or "docs"
    base = {
        "overseer_config_version": SUPPORTED_CONFIG_VERSION,
        "repo": {
            "name": repo_name,
            "root_relative_docs": docs_dir,
        },
        "thresholds": {
            "realign_max_commits": 50,
            "drift_warn_only": True,
        },
        "freeze_contract": {
            "enabled": True,
            "reviewer": {
                "mode": "agent",
                "model": "thinking-high",
                "provider": "local",
                "fallback": "human",
            },
            "human_escalation": ["security"],
        },
    }

    if regime == "git-only":
        base["vcs"] = {
            "regime": "git-only",
            "canonical": "git",
            "git": {
                "remote": "origin",
                "main_branch": "main",
                "mirror_branch": None,
                "feature_branch_pattern": "feat/{slug}",
            },
            "muse": {
                "staging_remote": None,
                "main_branch": None,
            },
        }
        base["docs"] = {
            "handover": "OVERSEER-HANDOVER.md",
            "roadmap": "ROADMAP.md",
            "coordination": None,
            "standing_decisions": "ROADMAP.md",
        }
        return base

    if regime == "muse-only":
        base["vcs"] = {
            "regime": "muse-only",
            "canonical": "muse",
            "git": {
                "remote": "origin",
                "main_branch": "main",
                "mirror_branch": None,
                "feature_branch_pattern": "feat/{slug}",
            },
            "muse": {
                "staging_remote": None,
                "main_branch": "main",
            },
        }
        base["docs"] = {
            "handover": "MUSEHUB-OVERSEER-HANDOVER.md",
            "roadmap": "MUSEHUB-ROADMAP.md",
            "coordination": None,
            "standing_decisions": "MUSEHUB-ROADMAP.md",
        }
        return base

    if regime == "muse+git-mirror":
        base["vcs"] = {
            "regime": "muse+git-mirror",
            "canonical": "muse",
            "git": {
                "remote": "origin",
                "main_branch": "main",
                "mirror_branch": "muse-mirror",
                "feature_branch_pattern": "feat/{slug}",
            },
            "muse": {
                "staging_remote": "staging",
                "main_branch": "main",
            },
        }
        base["docs"] = {
            "handover": "OVERSEER-HANDOVER.md",
            "roadmap": "ROADMAP.md",
            "coordination": "CROSS-REPO-COORDINATION.md",
            "standing_decisions": "CROSS-REPO-COORDINATION.md",
        }
        return base

    raise ConfigError(f"unsupported regime {regime!r}")


def config_dict_to_yaml(data: dict) -> str:
    """Serialize a config mapping to YAML text."""
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)


def load_config_from_dict(data: dict, path: str) -> OverseerConfig:
    """Validate a config dict via a temporary path label."""
    return load_config_from_text(config_dict_to_yaml(data), path)


def load_config_from_text(text: str, path: str) -> OverseerConfig:
    """Parse config text by writing to a temp file for ``load_config`` validation."""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        return load_config(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def configs_equal(a: OverseerConfig, b: OverseerConfig) -> bool:
    """Return True when two validated configs are equivalent."""
    return config_dict_to_yaml(config_to_dict(a)) == config_dict_to_yaml(config_to_dict(b))


def config_to_dict(config: OverseerConfig) -> dict:
    """Convert ``OverseerConfig`` back to a YAML-compatible mapping."""
    return {
        "overseer_config_version": config.overseer_config_version,
        "repo": {
            "name": config.repo.name,
            "root_relative_docs": config.repo.root_relative_docs,
        },
        "vcs": {
            "regime": config.vcs.regime,
            "canonical": config.vcs.canonical,
            "git": {
                "remote": config.vcs.git.remote,
                "main_branch": config.vcs.git.main_branch,
                "mirror_branch": config.vcs.git.mirror_branch,
                "feature_branch_pattern": config.vcs.git.feature_branch_pattern,
            },
            "muse": {
                "staging_remote": config.vcs.muse.staging_remote,
                "main_branch": config.vcs.muse.main_branch,
            },
        },
        "docs": {
            "handover": config.docs.handover,
            "roadmap": config.docs.roadmap,
            "coordination": config.docs.coordination,
            "standing_decisions": config.docs.standing_decisions,
        },
        "thresholds": {
            "realign_max_commits": config.thresholds.realign_max_commits,
            "drift_warn_only": config.thresholds.drift_warn_only,
        },
        "freeze_contract": {
            "enabled": config.freeze_contract.enabled,
            "reviewer": {
                "mode": config.freeze_contract.reviewer.mode,
                "model": config.freeze_contract.reviewer.model,
                "provider": config.freeze_contract.reviewer.provider,
                "fallback": config.freeze_contract.reviewer.fallback,
            },
            "human_escalation": list(config.freeze_contract.human_escalation),
        },
    }

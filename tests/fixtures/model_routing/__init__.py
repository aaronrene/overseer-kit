"""Shared fixtures for Track P / P-route tests (§PR.8)."""

from __future__ import annotations

from pathlib import Path

import yaml

from cli.kit_root import kit_root
from tests.support import FIXTURES, write_config


def copy_default_routing_policy(repo_root: Path, *, dest: str | None = None) -> Path:
    """Copy vendored routing policy into a test repo."""
    target_rel = dest or "policy/model-routing.yaml"
    source = kit_root() / "policy" / "model-routing.yaml"
    target = repo_root / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def seed_routing_repo(
    repo_root: Path,
    *,
    config_name: str = "config-git-only.yaml",
    policy_dest: str | None = None,
    enabled: bool = False,
    policy_path: str | None = None,
) -> Path:
    """Write config + routing policy for route CLI tests."""
    write_config(repo_root, config_name)
    policy_file = copy_default_routing_policy(repo_root, dest=policy_dest)
    if enabled or policy_path is not None:
        cfg_path = repo_root / ".overseer" / "config.yaml"
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        block: dict[str, object] = {"enabled": enabled}
        if policy_path is not None:
            block["policy"] = policy_path
        data["model_routing"] = block
        cfg_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return policy_file


def write_routing_policy(repo_root: Path, content: str, *, rel: str = "policy/model-routing.yaml") -> Path:
    """Write a custom routing policy file."""
    path = repo_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def minimal_valid_policy_yaml() -> str:
    return (kit_root() / "policy" / "model-routing.yaml").read_text(encoding="utf-8")


ROUTING_FIXTURES = FIXTURES / "model_routing"

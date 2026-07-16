"""Shared fixtures for Track P / P-cost tests (§PC.9)."""

from __future__ import annotations

from pathlib import Path

import yaml

from tests.fixtures.model_routing import copy_default_routing_policy, seed_routing_repo
from tests.support import FIXTURES, write_config


def seed_cost_awareness_repo(
    repo_root: Path,
    *,
    enabled: bool = True,
    surfaces: list[str] | None = None,
    config_name: str = "config-git-only.yaml",
) -> None:
    """Seed a repo with routing policy and optional cost-awareness config."""
    seed_routing_repo(repo_root, config_name=config_name)
    copy_default_routing_policy(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    block: dict[str, object] = {"enabled": enabled}
    if surfaces is not None:
        block["surfaces"] = surfaces
    data["cost_awareness"] = block
    cfg_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def seed_cost_e2e_repo(tmp_path: Path) -> None:
    """Fixture repo with handover/roadmap for active-slice spend-awareness e2e."""
    write_config(tmp_path, "config-governance-gates.yaml")
    copy_default_routing_policy(tmp_path)
    overseer = tmp_path / ".overseer"
    cfg_path = overseer / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["cost_awareness"] = {"enabled": True, "surfaces": ["status", "governance-sync"]}
    cfg_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    (overseer / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:0\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "cost-awareness-roadmap.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "cost-awareness-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "PHASE-DEMO-THINKING.md").write_text(
        (FIXTURES / "governance-gates-phase-thinking.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


COST_FIXTURES = FIXTURES / "cost_awareness"

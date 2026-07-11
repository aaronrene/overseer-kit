"""Integration: four pilot matrix configs load and resolve footprints (§K6.10)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from cli.footprint import resolve_footprint
from tests.support import PILOT


def test_scooling_config_loads_and_includes_coordination() -> None:
    config = load_config(PILOT / "config-scooling.yaml")
    assert config.vcs.regime == "muse+git-mirror"
    assert config.vcs.muse.working_dir is None
    dests = {f.destination for f in resolve_footprint(config)}
    assert "docs/CROSS-REPO-COORDINATION.md" in dests
    assert "docs/OVERSEER-HANDOVER.md" in dests
    assert "MUSE-BRIDGE-WORKFLOW.md" in dests
    assert "scripts/muse-bridge-deploy.sh" in dests


def test_knowtation_config_skips_coordination() -> None:
    config = load_config(PILOT / "config-knowtation.yaml")
    dests = {f.destination for f in resolve_footprint(config)}
    assert "docs/CROSS-REPO-COORDINATION.md" not in dests
    assert "docs/ROADMAP.md" in dests


def test_musehub_wires_working_dir() -> None:
    config = load_config(PILOT / "config-musehub.yaml")
    assert config.vcs.regime == "muse-only"
    assert config.vcs.muse.working_dir == "musehub"
    dests = {f.destination for f in resolve_footprint(config)}
    assert "docs/MUSEHUB-OVERSEER-HANDOVER.md" in dests
    assert "docs/MUSEHUB-ROADMAP.md" in dests


def test_videofactory_bare_paths_and_git_only() -> None:
    config = load_config(PILOT / "config-videofactory.yaml")
    assert config.vcs.regime == "git-only"
    assert config.repo.root_relative_docs == "."
    dests = {f.destination for f in resolve_footprint(config)}
    assert "OVERSEER_HANDOVER.md" in dests
    assert "ROADMAP.md" in dests


def test_all_pilot_configs_have_thresholds_and_nested_reviewer() -> None:
    for name in (
        "config-scooling.yaml",
        "config-knowtation.yaml",
        "config-musehub.yaml",
        "config-videofactory.yaml",
    ):
        config = load_config(PILOT / name)
        assert config.thresholds.realign_max_commits == 50
        assert config.freeze_contract.reviewer.mode == "agent"
        assert config.freeze_contract.reviewer.provider == "local"
        assert config.freeze_contract.reviewer.fallback == "human"

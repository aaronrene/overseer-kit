"""Unit tests for config schema validation fail-closed branches."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import SUPPORTED_CONFIG_VERSION, load_config
from adapters.errors import ConfigError
from tests.support import load_fixture_config, write_config


def test_load_valid_git_only_config(git_only_config) -> None:
    assert git_only_config.vcs.regime == "git-only"
    assert git_only_config.overseer_config_version == SUPPORTED_CONFIG_VERSION
    assert git_only_config.docs.handover_title == "Overseer Handover"
    assert git_only_config.docs.roadmap_title == "Roadmap"


def test_missing_config_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="missing"):
        load_config(tmp_path / ".overseer" / "config.yaml")


def test_unparseable_yaml_raises(tmp_path: Path) -> None:
    path = tmp_path / ".overseer" / "config.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(":\n  bad:\n- yaml", encoding="utf-8")
    with pytest.raises(ConfigError, match="unparseable"):
        load_config(path)


def test_unknown_config_version_raises(repo_root: Path) -> None:
    path = write_config(repo_root, "config-git-only.yaml")
    text = path.read_text(encoding="utf-8").replace(
        "overseer_config_version: 1",
        "overseer_config_version: 99",
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match="unsupported overseer_config_version"):
        load_config(path)


def test_unknown_regime_raises(repo_root: Path) -> None:
    path = write_config(repo_root, "config-git-only.yaml")
    text = path.read_text(encoding="utf-8").replace(
        "regime: git-only",
        "regime: svn-only",
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match="unsupported vcs.regime"):
        load_config(path)


def test_git_only_with_muse_fields_raises(repo_root: Path) -> None:
    path = write_config(repo_root, "config-git-only.yaml")
    text = path.read_text(encoding="utf-8").replace(
        "main_branch: null",
        'main_branch: "main"',
        1,
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match="muse fields to be null"):
        load_config(path)


def test_muse_git_mirror_missing_mirror_branch_raises(repo_root: Path) -> None:
    path = write_config(repo_root, "config-muse-git-mirror.yaml")
    text = path.read_text(encoding="utf-8").replace(
        "mirror_branch: muse-mirror",
        "mirror_branch: null",
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match="mirror_branch"):
        load_config(path)


def test_load_two_lane_config(repo_root: Path) -> None:
    cfg = load_fixture_config(repo_root, "config-two-lane.yaml")
    assert cfg.docs.default_lane == "queue"
    assert cfg.docs.lanes is not None
    assert set(cfg.docs.lanes) == {"queue", "active"}
    assert cfg.docs.lanes["active"].handover == "videos/_active/HANDOVER.md"


def test_lanes_default_lane_mismatch_raises(repo_root: Path) -> None:
    path = write_config(repo_root, "config-two-lane.yaml")
    text = path.read_text(encoding="utf-8").replace(
        "handover: QUEUE_HANDOVER.md",
        "handover: WRONG.md",
        1,
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match="must match docs.lanes"):
        load_config(path)


def test_resolve_lane_docs_single_lane(git_only_config) -> None:
    from adapters.config import resolve_lane_docs

    docs = resolve_lane_docs(git_only_config, None)
    assert docs.handover == git_only_config.docs.handover


def test_resolve_lane_docs_unknown_lane_raises(repo_root: Path) -> None:
    from adapters.config import resolve_lane_docs

    cfg = load_fixture_config(repo_root, "config-two-lane.yaml")
    with pytest.raises(ConfigError, match="unknown lane"):
        resolve_lane_docs(cfg, "missing")

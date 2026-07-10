"""Shared pytest fixtures for adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import OverseerConfig
from tests.support import load_fixture_config, write_config


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    (tmp_path / ".overseer").mkdir()
    return tmp_path


@pytest.fixture
def git_only_config(repo_root: Path) -> OverseerConfig:
    return load_fixture_config(repo_root, "config-git-only.yaml")


@pytest.fixture
def muse_only_config(repo_root: Path) -> OverseerConfig:
    return load_fixture_config(repo_root, "config-muse-only.yaml")


@pytest.fixture
def muse_git_mirror_config(repo_root: Path) -> OverseerConfig:
    return load_fixture_config(repo_root, "config-muse-git-mirror.yaml")

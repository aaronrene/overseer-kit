"""Unit tests for Muse substrate health checks."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from tests.support import FIXTURES
from tools.substrate_health import check_substrate


def test_git_only_not_applicable(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    report = check_substrate(config, tmp_path)
    assert report.ok
    assert report.state == "not_applicable"


def test_muse_mirror_healthy(repo_root: Path, muse_git_mirror_config) -> None:
    muse = repo_root / ".muse"
    muse.mkdir(parents=True)
    (muse / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (muse / "repo.json").write_text("{}", encoding="utf-8")
    (muse / "config.toml").write_text("", encoding="utf-8")
    report = check_substrate(muse_git_mirror_config, repo_root)
    assert report.ok
    assert report.state == "healthy"


def test_muse_mirror_hollow(repo_root: Path, muse_git_mirror_config) -> None:
    (repo_root / ".muse").mkdir(parents=True)
    (repo_root / ".museattributes").write_text("", encoding="utf-8")
    report = check_substrate(muse_git_mirror_config, repo_root)
    assert not report.ok
    assert report.state == "hollow"
    assert report.remediation == "muse init --force ."
    assert ".muse/HEAD" in report.missing


def test_muse_mirror_missing_dir(repo_root: Path, muse_git_mirror_config) -> None:
    report = check_substrate(muse_git_mirror_config, repo_root)
    assert not report.ok
    assert report.state == "missing"
    assert report.remediation == "muse init ."

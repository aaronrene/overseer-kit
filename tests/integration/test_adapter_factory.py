"""Integration tests — config + factory + adapter composition."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters import load_adapter
from adapters.errors import ConfigError, ReadError
from adapters.git_only.adapter import GitOnlyAdapter
from adapters.muse_git_mirror.adapter import MuseGitMirrorAdapter
from adapters.muse_only.adapter import MuseOnlyAdapter
from tests.support import fail, make_runner, ok, write_config


def test_load_adapter_git_only(repo_root: Path) -> None:
    write_config(repo_root, "config-git-only.yaml")
    runner = make_runner(
        {
            "git rev-parse": ok("main"),
            "git status": ok(""),
        }
    )
    adapter = load_adapter(repo_root, runner=runner)
    assert isinstance(adapter, GitOnlyAdapter)
    status = adapter.status()
    assert status.branch == "main"


def test_load_adapter_muse_only(repo_root: Path) -> None:
    write_config(repo_root, "config-muse-only.yaml")
    root = str(repo_root.resolve())
    runner = make_runner(
        {
            f"muse -C {root} branch": ok("main"),
            f"muse -C {root} status": ok(""),
        }
    )
    adapter = load_adapter(repo_root, runner=runner)
    assert isinstance(adapter, MuseOnlyAdapter)


def test_load_adapter_muse_git_mirror(repo_root: Path) -> None:
    write_config(repo_root, "config-muse-git-mirror.yaml")
    root = str(repo_root.resolve())
    runner = make_runner(
        {
            f"muse -C {root} branch": ok("main"),
            f"muse -C {root} status": ok(""),
            "git rev-parse": ok("main"),
            "git status": ok(""),
        }
    )
    adapter = load_adapter(repo_root, runner=runner)
    assert isinstance(adapter, MuseGitMirrorAdapter)


def test_load_adapter_missing_config(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_adapter(tmp_path)


def test_end_to_end_read_head_chain_fails_closed(repo_root: Path) -> None:
    write_config(repo_root, "config-git-only.yaml")
    runner = make_runner({"git rev-parse": fail("network down")})
    adapter = load_adapter(repo_root, runner=runner)
    result = adapter.read_head("origin/main")
    assert isinstance(result, ReadError)
    assert result.exit_code == 1

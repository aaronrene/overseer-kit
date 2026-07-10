"""Unit tests for git-only adapter fail-closed branches."""

from __future__ import annotations

from adapters.errors import ReadError, WriteError
from tests.support import adapter_for, fail, make_runner, ok


def test_status_success(git_only_config, repo_root) -> None:
    runner = make_runner(
        {
            "git rev-parse": ok("feat/test"),
            "git status": ok(""),
        }
    )
    adapter = adapter_for(git_only_config, repo_root, runner)
    result = adapter.status()
    assert result.regime == "git-only"
    assert result.branch == "feat/test"
    assert result.dirty is False


def test_status_fails_closed_on_git_error(git_only_config, repo_root) -> None:
    runner = make_runner({"git rev-parse": fail("fatal: not a git repo")})
    adapter = adapter_for(git_only_config, repo_root, runner)
    result = adapter.status()
    assert isinstance(result, ReadError)
    assert "git rev-parse" in result.command


def test_read_head_missing_ref(git_only_config, repo_root) -> None:
    runner = make_runner({"git rev-parse": fail("bad ref", 128)})
    adapter = adapter_for(git_only_config, repo_root, runner)
    result = adapter.read_head("origin/main")
    assert isinstance(result, ReadError)


def test_read_head_rejects_muse_ref(git_only_config, repo_root) -> None:
    adapter = adapter_for(git_only_config, repo_root, make_runner({}))
    result = adapter.read_head("muse:main")
    assert isinstance(result, ReadError)
    assert "forbidden" in result.message


def test_read_canonical_anchor(git_only_config, repo_root) -> None:
    runner = make_runner({"git rev-parse": ok("abc123def456")})
    adapter = adapter_for(git_only_config, repo_root, runner)
    result = adapter.read_canonical_anchor()
    assert result.anchor_sha == "abc123def456"
    assert result.source == "origin/main"


def test_realign_noop(git_only_config, repo_root) -> None:
    adapter = adapter_for(git_only_config, repo_root, make_runner({}))
    result = adapter.realign(dry_run=True, max_commits=50)
    assert result.applied is False
    assert result.reason == "single-history"


def test_commit_feature_refuses_main(git_only_config, repo_root) -> None:
    adapter = adapter_for(git_only_config, repo_root, make_runner({}))
    result = adapter.commit_feature(branch="main", message="x", paths=["docs/a.md"])
    assert isinstance(result, WriteError)
    assert "protected" in result.message


def test_commit_feature_unsafe_path(git_only_config, repo_root) -> None:
    adapter = adapter_for(git_only_config, repo_root, make_runner({}))
    result = adapter.commit_feature(
        branch="feat/x",
        message="x",
        paths=["../escape"],
    )
    assert isinstance(result, ReadError)
    assert "unsafe path" in result.message


def test_mirror_noop(git_only_config, repo_root) -> None:
    adapter = adapter_for(git_only_config, repo_root, make_runner({}))
    result = adapter.mirror(dry_run=True)
    assert result.pushed is False
    assert result.reason == "single-history"

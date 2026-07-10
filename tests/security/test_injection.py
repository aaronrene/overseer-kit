"""Security tests — injection surfaces in adapter inputs."""

from __future__ import annotations

from adapters.errors import ReadError, WriteError
from tests.support import adapter_for, make_runner, ok


def test_commit_feature_rejects_path_traversal(git_only_config, repo_root) -> None:
    adapter = adapter_for(git_only_config, repo_root, make_runner({}))
    result = adapter.commit_feature(
        branch="feat/x",
        message="ok",
        paths=["../../etc/passwd"],
    )
    assert isinstance(result, ReadError)


def test_commit_feature_rejects_dash_prefixed_path(muse_only_config, repo_root) -> None:
    adapter = adapter_for(muse_only_config, repo_root, make_runner({}))
    result = adapter.commit_feature(
        branch="feat/x",
        message="ok",
        paths=["-rf"],
    )
    assert isinstance(result, ReadError)


def test_commit_feature_refuses_protected_main_across_regimes(
    git_only_config,
    muse_only_config,
    muse_git_mirror_config,
    repo_root,
) -> None:
    for config in (git_only_config, muse_only_config, muse_git_mirror_config):
        adapter = adapter_for(config, repo_root, make_runner({}))
        result = adapter.commit_feature(branch="main", message="x", paths=[])
        assert isinstance(result, WriteError)


def test_shell_metacharacters_are_quoted(git_only_config, repo_root) -> None:
    runner = make_runner(
        {
            "git checkout": ok(""),
            "git add": ok(""),
            "git commit": ok(""),
            "git rev-parse": ok("deadbeef"),
        }
    )
    adapter = adapter_for(git_only_config, repo_root, runner)
    branch = "feat/$(rm -rf /)"
    adapter.commit_feature(branch=branch, message="safe", paths=["docs/a.md"])
    checkout_cmds = [c[0] for c in runner.calls if "git checkout" in c[0]]
    assert checkout_cmds == [f"git checkout 'feat/$(rm -rf /)'"]

"""Security tests — least-privilege regime enforcement."""

from __future__ import annotations

from adapters.errors import ReadError
from tests.support import adapter_for, make_runner, ok


def test_muse_only_never_invokes_git(muse_only_config, repo_root) -> None:
    runner = make_runner({})
    adapter = adapter_for(muse_only_config, repo_root, runner)
    adapter.mirror(dry_run=False)
    adapter.read_head("origin/main")
    assert all("git " not in call[0] for call in runner.calls)


def test_git_only_rejects_muse_refs_without_subprocess(git_only_config, repo_root) -> None:
    runner = make_runner({})
    adapter = adapter_for(git_only_config, repo_root, runner)
    result = adapter.read_head("muse:main")
    assert isinstance(result, ReadError)
    assert runner.calls == []


def test_muse_git_mirror_uses_absolute_repo_root(muse_git_mirror_config, repo_root) -> None:
    root = str(repo_root.resolve())
    runner = make_runner(
        {
            f"muse -C {root} branch": ok("main"),
            f"muse -C {root} status": ok(""),
            "git rev-parse": ok("main"),
            "git status": ok(""),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    adapter.status()
    muse_calls = [c for c in runner.calls if c[0].startswith("muse -C")]
    assert muse_calls
    for command, _cwd in muse_calls:
        assert root in command
        assert "muse -C ." not in command


def test_muse_only_mirror_never_pushes(muse_only_config, repo_root) -> None:
    runner = make_runner({})
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.mirror(dry_run=False)
    assert result.pushed is False

"""Security tests — fail-closed read behavior."""

from __future__ import annotations

from adapters.errors import ReadError
from tests.support import adapter_for, fail, make_runner, ok


def test_git_status_error_surfaces_exact_command(git_only_config, repo_root) -> None:
    runner = make_runner(
        {
            "git rev-parse": ok("main"),
            "git status": fail("permission denied", 128),
        }
    )
    adapter = adapter_for(git_only_config, repo_root, runner)
    result = adapter.status()
    assert isinstance(result, ReadError)
    assert "git status" in result.command
    assert result.exit_code == 128


def test_muse_read_head_never_fabricates_sha(muse_only_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner({f"muse -C {root} log": fail("ref missing")})
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.read_head("muse:main")
    assert isinstance(result, ReadError)


def test_muse_git_mirror_realign_missing_anchor_is_read_error(
    muse_git_mirror_config,
    repo_root,
) -> None:
    adapter = adapter_for(muse_git_mirror_config, repo_root, make_runner({}))
    result = adapter.realign(dry_run=True, max_commits=50)
    assert isinstance(result, ReadError)


def test_mirror_git_import_failure_propagates(muse_git_mirror_config, repo_root) -> None:
    bridge = repo_root / ".muse"
    bridge.mkdir(parents=True)
    (bridge / "git-bridge.toml").write_text(
        '[last_import]\ngit_sha = "abc"\n',
        encoding="utf-8",
    )
    root = str(repo_root)
    runner = make_runner(
        {
            "git rev-parse": ok("def"),
            "git rev-list": ok("1"),
            f"muse -C {root} bridge": fail("import failed"),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.realign(dry_run=False, max_commits=50)
    assert isinstance(result, ReadError)

"""Unit tests for muse-only adapter fail-closed branches."""

from __future__ import annotations

from adapters.errors import ReadError, WriteError
from tests.support import adapter_for, fail, make_runner, ok

GIT_FORBIDDEN = "git forbidden in this regime"


def test_status_success(muse_only_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner(
        {
            f"muse -C {root} branch": ok("feat/hub"),
            f"muse -C {root} status --json": ok('{"dirty": false, "branch": "feat/hub"}'),
        }
    )
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.status()
    assert result.regime == "muse-only"
    assert result.branch == "feat/hub"
    assert "git-forbidden" in result.notes[1]


def test_status_fails_closed_on_muse_error(muse_only_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner({f"muse -C {root} branch": fail("muse unavailable")})
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.status()
    assert isinstance(result, ReadError)
    assert "muse -C" in result.command


def test_read_head_rejects_git_ref(muse_only_config, repo_root) -> None:
    adapter = adapter_for(muse_only_config, repo_root, make_runner({}))
    result = adapter.read_head("origin/main")
    assert isinstance(result, ReadError)
    assert result.message == GIT_FORBIDDEN


def test_read_canonical_anchor(muse_only_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner({f"muse -C {root} log": ok("sha256:abc")})
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.read_canonical_anchor()
    assert result.anchor_sha == "sha256:abc"
    assert result.source == "muse:main"


def test_realign_noop(muse_only_config, repo_root) -> None:
    adapter = adapter_for(muse_only_config, repo_root, make_runner({}))
    result = adapter.realign(dry_run=False, max_commits=50)
    assert result.reason == "single-history"


def test_mirror_reports_git_forbidden(muse_only_config, repo_root) -> None:
    adapter = adapter_for(muse_only_config, repo_root, make_runner({}))
    result = adapter.mirror(dry_run=True)
    assert result.reason == GIT_FORBIDDEN
    assert result.pushed is False


def test_commit_feature_refuses_main(muse_only_config, repo_root) -> None:
    adapter = adapter_for(muse_only_config, repo_root, make_runner({}))
    result = adapter.commit_feature(branch="main", message="x", paths=[])
    assert isinstance(result, WriteError)

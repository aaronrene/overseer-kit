"""Unit tests for muse+git-mirror adapter fail-closed branches."""

from __future__ import annotations

from pathlib import Path

from adapters.errors import ReadError
from tests.support import adapter_for, fail, make_runner, ok


def _bridge_toml(from_sha: str = "aaa111", export_sha: str = "bbb222") -> str:
    return f"""[last_import]
git_sha = "{from_sha}"

[last_export]
git_sha = "{export_sha}"
"""


def test_status_reads_both_histories(muse_git_mirror_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": false}'),
            f"muse -C {root} status --porcelain": ok(""),
            "git rev-parse": ok("main"),
            "git status": ok(" M file"),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.status()
    assert result.dirty is True
    assert "sd-14" in result.notes[2]


def test_read_canonical_anchor_from_bridge(muse_git_mirror_config, repo_root) -> None:
    bridge = repo_root / ".muse"
    bridge.mkdir(parents=True)
    (bridge / "git-bridge.toml").write_text(_bridge_toml(), encoding="utf-8")
    adapter = adapter_for(muse_git_mirror_config, repo_root, make_runner({}))
    result = adapter.read_canonical_anchor()
    assert result.anchor_sha == "bbb222"
    assert "last_export" in result.source


def test_read_canonical_anchor_fails_without_bridge(muse_git_mirror_config, repo_root) -> None:
    runner = make_runner({"git rev-parse": fail("unknown ref")})
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.read_canonical_anchor()
    assert isinstance(result, ReadError)


def test_realign_dry_run_counts_commits(muse_git_mirror_config, repo_root) -> None:
    bridge = repo_root / ".muse"
    bridge.mkdir(parents=True)
    (bridge / "git-bridge.toml").write_text(_bridge_toml(from_sha="aaa"), encoding="utf-8")
    runner = make_runner(
        {
            "git rev-parse": ok("ccc333"),
            "git rev-list": ok("3"),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.realign(dry_run=True, max_commits=50)
    assert result.would_import == 3
    assert result.applied is False
    assert result.reason == "dry-run"


def test_realign_refuses_over_max_commits(muse_git_mirror_config, repo_root) -> None:
    bridge = repo_root / ".muse"
    bridge.mkdir(parents=True)
    (bridge / "git-bridge.toml").write_text(_bridge_toml(), encoding="utf-8")
    runner = make_runner(
        {
            "git rev-parse": ok("ccc333"),
            "git rev-list": ok("99"),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.realign(dry_run=False, max_commits=50)
    assert result.would_import == 99
    assert result.applied is False
    assert "max_commits" in (result.reason or "")


def test_realign_apply_invokes_git_import(muse_git_mirror_config, repo_root) -> None:
    bridge = repo_root / ".muse"
    bridge.mkdir(parents=True)
    (bridge / "git-bridge.toml").write_text(_bridge_toml(), encoding="utf-8")
    root = str(repo_root)
    runner = make_runner(
        {
            "git rev-parse": ok("ccc333"),
            "git rev-list": ok("2"),
            f"muse -C {root} bridge": ok("imported"),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.realign(dry_run=False, max_commits=50)
    assert result.applied is True
    assert any("git-import" in call[0] for call in runner.calls)


def test_mirror_dry_run_reports_delta(muse_git_mirror_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner({f"muse -C {root} bridge": ok("2 commits ahead")})
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.mirror(dry_run=True)
    assert result.diff_summary == "2 commits ahead"
    assert result.pushed is False


def test_mirror_requires_operator_before_push(muse_git_mirror_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner({f"muse -C {root} bridge": ok("ready")})
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.mirror(dry_run=False)
    assert result.pushed is False
    assert result.reason == "operator-authorization-required"


def test_commit_feature_uses_rev_parse_for_branch_probe(muse_git_mirror_config, repo_root) -> None:
    """muse 0.2.0rc15 lacks ``branch --show-current``; probe via ``rev-parse --abbrev-ref HEAD``."""
    root = str(repo_root)
    runner = make_runner(
        {
            f"muse -C {root} checkout": ok(""),
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("feat/k7"),
            f"muse -C {root} commit": ok(""),
            f"muse -C {root} log -1 --format=%H": ok("sha256:abc"),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.commit_feature(branch="feat/k7", message="test", paths=[])
    assert result.committed is True
    assert any("rev-parse --abbrev-ref HEAD" in call[0] for call in runner.calls)
    assert not any("branch --show-current" in call[0] for call in runner.calls)

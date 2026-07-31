"""Unit tier §PLS.10 — config parse, trigger matrix, dirty skip, checkout, exit 36."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import PostLandSyncConfig, load_config
from adapters.errors import ConfigError
from tests.support import FIXTURES, FakeGitRunner, gh_merged_runner, pls_config
from tools.close_ritual.post_land_sync import run_post_land_sync
from tools.close_ritual.pr_land import (
    EXIT_CHECKS_FAILED,
    EXIT_OK,
    EXIT_POST_LAND_SYNC,
    run_pr_land,
)


def _write_config(repo_root: Path, close_ritual_block: str) -> Path:
    base = (FIXTURES / "config-git-only.yaml").read_text(encoding="utf-8")
    dest = repo_root / ".overseer" / "config.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(base + "\n" + close_ritual_block, encoding="utf-8")
    return dest


# --- Config parse (§PLS.3.2 — fail-closed) ---


def test_defaults_when_block_omitted(tmp_path: Path) -> None:
    config = load_config(_write_config(tmp_path, ""))
    assert config.close_ritual.post_land_sync == PostLandSyncConfig(
        enabled=False, strategy="ff_only", require_clean_worktree=True
    )


def test_defaults_when_post_land_sync_omitted(tmp_path: Path) -> None:
    config = load_config(_write_config(tmp_path, "close_ritual:\n  enabled: false\n"))
    assert config.close_ritual.post_land_sync.enabled is False
    assert config.close_ritual.post_land_sync.strategy == "ff_only"
    assert config.close_ritual.post_land_sync.require_clean_worktree is True


def test_parse_explicit_opt_in(tmp_path: Path) -> None:
    config = load_config(
        _write_config(
            tmp_path,
            "close_ritual:\n"
            "  post_land_sync:\n"
            "    enabled: true\n"
            "    strategy: ff_only\n"
            "    require_clean_worktree: true\n",
        )
    )
    assert config.close_ritual.post_land_sync.enabled is True


@pytest.mark.parametrize(
    "block, fragment",
    [
        (
            "close_ritual:\n  post_land_sync:\n    surprise: 1\n",
            "unknown close_ritual.post_land_sync keys",
        ),
        (
            "close_ritual:\n  post_land_sync:\n    strategy: rebase\n",
            "strategy must be ff_only",
        ),
        (
            "close_ritual:\n  post_land_sync:\n    require_clean_worktree: false\n",
            "require_clean_worktree must be true",
        ),
        (
            "close_ritual:\n  post_land_sync:\n    enabled: yes please\n",
            "enabled must be a boolean",
        ),
        (
            "close_ritual:\n  post_land_sync:\n    require_clean_worktree: sometimes\n",
            "require_clean_worktree must be true",
        ),
    ],
)
def test_parse_rejects_bad_values(tmp_path: Path, block: str, fragment: str) -> None:
    with pytest.raises(ConfigError) as excinfo:
        load_config(_write_config(tmp_path, block))
    assert fragment in str(excinfo.value)


# --- Trigger matrix (§PLS.4.1) ---


def test_enabled_merged_not_dry_run_enters_helper(repo_root: Path) -> None:
    git = FakeGitRunner(branch="main")
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_OK
    assert result.post_land_sync["status"] == "synced"
    assert git.calls[0] == ["git", "fetch", "origin"]


def test_no_config_defaults_to_disabled_always_present(repo_root: Path) -> None:
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
    )
    assert result.exit_code == EXIT_OK
    assert result.post_land_sync == {
        "status": "disabled",
        "remote": "",
        "main_branch": "",
        "messages": [],
    }
    assert "post_land_sync" in result.to_dict()


def test_disabled_config_no_git_argv(repo_root: Path) -> None:
    git = FakeGitRunner()
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root, enabled=False),
        git_runner=git,
    )
    assert result.post_land_sync["status"] == "disabled"
    assert git.calls == []


def test_dry_run_never_syncs(repo_root: Path) -> None:
    git = FakeGitRunner()
    result = run_pr_land(
        "1",
        authorization="operator: land",
        dry_run=True,
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_OK
    assert result.merged is False
    assert result.post_land_sync["status"] == "not_applicable"
    assert git.calls == []


def test_checks_failed_never_syncs(repo_root: Path) -> None:
    git = FakeGitRunner()
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(check_state="fail"),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_CHECKS_FAILED
    assert result.post_land_sync["status"] == "not_applicable"
    assert git.calls == []


def test_already_merged_checks_failed_never_syncs(repo_root: Path) -> None:
    git = FakeGitRunner()
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(pr_state="MERGED", check_state="fail"),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_CHECKS_FAILED
    assert result.already_merged is True
    assert result.post_land_sync["status"] == "not_applicable"
    assert git.calls == []


def test_muse_only_regime_skipped_zero_git_argv(repo_root: Path) -> None:
    git = FakeGitRunner()
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root, "config-muse-only.yaml"),
        git_runner=git,
    )
    assert result.exit_code == EXIT_OK
    assert result.post_land_sync["status"] == "regime_skipped"
    assert result.post_land_sync["remote"] == ""
    assert result.post_land_sync["main_branch"] == ""
    assert git.calls == []


# --- Dirty skip / checkout / hard-fail (§PLS.4.2, §PLS.5, §PLS.6) ---


def test_dirty_porcelain_skips_without_checkout_or_pull(repo_root: Path) -> None:
    git = FakeGitRunner(porcelain=" M docs/OVERSEER-HANDOVER.md\n?? scratch.txt\n")
    report = run_post_land_sync(
        repo_root=repo_root,
        regime="git-only",
        remote="origin",
        main_branch="main",
        git_runner=git,
    )
    assert report.status == "skipped_dirty"
    ops = [c[1] for c in git.calls]
    assert "checkout" not in ops
    assert "pull" not in ops
    assert any("dirty" in m for m in report.messages)


def test_clean_on_feature_branch_checks_out_main_then_ff_pull(repo_root: Path) -> None:
    git = FakeGitRunner(branch="feat/pls-a")
    report = run_post_land_sync(
        repo_root=repo_root,
        regime="git-only",
        remote="origin",
        main_branch="main",
        git_runner=git,
    )
    assert report.status == "synced"
    assert ["git", "checkout", "main"] in git.calls
    checkout_idx = git.calls.index(["git", "checkout", "main"])
    pull_idx = git.calls.index(["git", "pull", "--ff-only", "origin", "main"])
    assert checkout_idx < pull_idx


@pytest.mark.parametrize("failing_op", ["fetch", "status", "checkout", "pull"])
def test_hard_fail_maps_to_exit_36_not_6(repo_root: Path, failing_op: str) -> None:
    git = FakeGitRunner(branch="feat/pls-a", fail={failing_op})
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_POST_LAND_SYNC
    assert result.exit_code == 36
    assert result.exit_code != 6
    assert result.merged is True
    assert result.post_land_sync["status"] == "failed"


def test_missing_repo_root_when_enabled_hard_fails(repo_root: Path) -> None:
    git = FakeGitRunner()
    result = run_pr_land(
        "1",
        authorization="operator: land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=None,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_POST_LAND_SYNC
    assert result.post_land_sync["status"] == "failed"
    assert git.calls == []

"""Integration tier §PLS.10 — merge engine + sync helper compose via injected runners."""

from __future__ import annotations

from pathlib import Path

from tests.support import FakeGitRunner, gh_merged_runner, pls_config
from tools.close_ritual.post_land_sync import EDITOR_BUFFER_NOTE
from tools.close_ritual.pr_land import EXIT_OK, run_pr_land


def test_successful_merge_then_ff_only_pull_reports_synced(repo_root: Path) -> None:
    git = FakeGitRunner(branch="feat/pls-a")
    result = run_pr_land(
        "7",
        authorization="operator: land PLS",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_OK
    assert result.merged is True
    assert result.post_land_sync["status"] == "synced"
    assert result.post_land_sync["remote"] == "origin"
    assert result.post_land_sync["main_branch"] == "main"
    # Mocked main tip updated via fetch + ff-only pull argv (frozen §PLS.4.2).
    assert ["git", "fetch", "origin"] in git.calls
    assert ["git", "pull", "--ff-only", "origin", "main"] in git.calls
    # Editor-buffer note present in both message surfaces (§PLS.4.4 / §PLS.6.3).
    assert EDITOR_BUFFER_NOTE in result.post_land_sync["messages"]
    assert EDITOR_BUFFER_NOTE in result.messages


def test_already_merged_path_also_invokes_sync_when_enabled(repo_root: Path) -> None:
    git = FakeGitRunner(branch="main")
    result = run_pr_land(
        "7",
        authorization="operator: re-run after land",
        runner=gh_merged_runner(pr_state="MERGED"),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=git,
    )
    assert result.exit_code == EXIT_OK
    assert result.already_merged is True
    assert result.post_land_sync["status"] == "synced"
    assert ["git", "fetch", "origin"] in git.calls
    assert ["git", "pull", "--ff-only", "origin", "main"] in git.calls


def test_muse_git_mirror_regime_runs_git_side_only(repo_root: Path) -> None:
    git = FakeGitRunner(branch="main")
    result = run_pr_land(
        "7",
        authorization="operator: land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root, "config-muse-git-mirror.yaml"),
        git_runner=git,
    )
    assert result.post_land_sync["status"] == "synced"
    # Git side only — never Muse commits, bridge export, or muse pull (§PLS.5.3).
    assert all(call[0] == "git" for call in git.calls)

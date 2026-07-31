"""Performance tier §PLS.10 — bounded git calls; no unbounded log walks."""

from __future__ import annotations

import time
from pathlib import Path

from tests.support import FakeGitRunner
from tools.close_ritual.post_land_sync import run_post_land_sync

# Frozen §PLS.4.2 sequence: fetch + status + branch read + optional checkout + pull.
MAX_GIT_CALLS = 5


def test_clean_sync_on_main_uses_bounded_calls(repo_root: Path) -> None:
    git = FakeGitRunner(branch="main")
    run_post_land_sync(
        repo_root=repo_root,
        regime="git-only",
        remote="origin",
        main_branch="main",
        git_runner=git,
    )
    assert len(git.calls) <= MAX_GIT_CALLS - 1  # no checkout needed on main
    assert all(call[1] != "log" for call in git.calls)


def test_clean_sync_on_feature_branch_uses_bounded_calls(repo_root: Path) -> None:
    git = FakeGitRunner(branch="feat/pls-perf")
    run_post_land_sync(
        repo_root=repo_root,
        regime="git-only",
        remote="origin",
        main_branch="main",
        git_runner=git,
    )
    assert len(git.calls) <= MAX_GIT_CALLS


def test_dirty_skip_stops_after_status(repo_root: Path) -> None:
    git = FakeGitRunner(porcelain=" M big-file.md\n" * 500)
    run_post_land_sync(
        repo_root=repo_root,
        regime="git-only",
        remote="origin",
        main_branch="main",
        git_runner=git,
    )
    assert len(git.calls) == 2  # fetch + status only


def test_many_runs_complete_under_unit_budget(repo_root: Path) -> None:
    started = time.monotonic()
    for _ in range(200):
        run_post_land_sync(
            repo_root=repo_root,
            regime="git-only",
            remote="origin",
            main_branch="main",
            git_runner=FakeGitRunner(branch="main"),
        )
    assert time.monotonic() - started < 2.0

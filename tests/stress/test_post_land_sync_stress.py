"""Stress tier §PLS.10 — N≥20 alternating dirty-skip / clean-sync cycles."""

from __future__ import annotations

from pathlib import Path

from tests.support import FakeGitRunner
from tools.close_ritual.post_land_sync import run_post_land_sync

FORBIDDEN_TOKENS = ("--force", "reset", "clean", "stash", "merge", "push", "gh")
ALLOWED_OPS = {"fetch", "status", "rev-parse", "checkout", "pull"}


def test_alternating_dirty_and_clean_cycles_never_clobber(repo_root: Path) -> None:
    cycles = 24
    for i in range(cycles):
        dirty = i % 2 == 0
        git = FakeGitRunner(
            porcelain=f" M docs/file-{i}.md\n" if dirty else "",
            branch="feat/pls-stress" if i % 4 == 1 else "main",
        )
        report = run_post_land_sync(
            repo_root=repo_root,
            regime="git-only",
            remote="origin",
            main_branch="main",
            git_runner=git,
        )
        ops = [c[1] for c in git.calls]
        if dirty:
            # Never clobber: no checkout/pull after a dirty porcelain read.
            assert report.status == "skipped_dirty"
            assert "checkout" not in ops
            assert "pull" not in ops
        else:
            assert report.status == "synced"
            assert git.calls[-1] == ["git", "pull", "--ff-only", "origin", "main"]
        for call in git.calls:
            assert call[0] == "git"
            assert call[1] in ALLOWED_OPS
            for token in FORBIDDEN_TOKENS:
                assert token not in call[1:]

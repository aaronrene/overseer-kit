"""E2E tier §PLS.10 — real temp git repos: land stubbed to merged, sync via real git."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.support import gh_merged_runner, pls_config
from tools.close_ritual.pr_land import EXIT_OK, run_pr_land


def _git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


@pytest.fixture
def land_repos(tmp_path: Path) -> tuple[Path, Path]:
    """Return ``(work, origin)``: a clone plus a bare origin one commit ahead on main."""
    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare", "-b", "main")

    work = tmp_path / "work"
    _git(tmp_path, "clone", str(origin), "work")
    _git(work, "config", "user.email", "test@example.com")
    _git(work, "config", "user.name", "test")
    (work / "docs").mkdir()
    (work / "docs" / "HANDOVER.md").write_text("v1\n", encoding="utf-8")
    # Keep the test-harness config out of porcelain so "clean tree" means clean.
    (work / ".gitignore").write_text(".overseer/\n", encoding="utf-8")
    _git(work, "add", ".")
    _git(work, "commit", "-m", "seed")
    _git(work, "push", "-u", "origin", "main")

    # Simulate the PR landing on GitHub main from elsewhere.
    other = tmp_path / "other"
    _git(tmp_path, "clone", str(origin), "other")
    _git(other, "config", "user.email", "test@example.com")
    _git(other, "config", "user.name", "test")
    (other / "docs" / "HANDOVER.md").write_text("v2 landed\n", encoding="utf-8")
    _git(other, "add", ".")
    _git(other, "commit", "-m", "landed PR")
    _git(other, "push", "origin", "main")

    (work / ".overseer").mkdir()
    return work, origin


def test_clean_feature_branch_ends_on_main_matching_origin(
    land_repos: tuple[Path, Path],
) -> None:
    work, _origin = land_repos
    _git(work, "checkout", "-b", "feat/pls-work")

    result = run_pr_land(
        "9",
        authorization="operator: e2e land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=work,
        config=pls_config(work),
    )

    assert result.exit_code == EXIT_OK
    assert result.post_land_sync["status"] == "synced"
    assert _git(work, "rev-parse", "--abbrev-ref", "HEAD") == "main"
    assert _git(work, "rev-parse", "main") == _git(work, "rev-parse", "origin/main")
    assert (work / "docs" / "HANDOVER.md").read_text(encoding="utf-8") == "v2 landed\n"


def test_dirty_tree_skips_head_unchanged_exit_zero(land_repos: tuple[Path, Path]) -> None:
    work, _origin = land_repos
    _git(work, "checkout", "-b", "feat/pls-dirty")
    (work / "docs" / "HANDOVER.md").write_text("uncommitted local edits\n", encoding="utf-8")
    head_before = _git(work, "rev-parse", "HEAD")

    result = run_pr_land(
        "9",
        authorization="operator: e2e dirty land",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=work,
        config=pls_config(work),
    )

    assert result.exit_code == EXIT_OK
    assert result.post_land_sync["status"] == "skipped_dirty"
    assert _git(work, "rev-parse", "--abbrev-ref", "HEAD") == "feat/pls-dirty"
    assert _git(work, "rev-parse", "HEAD") == head_before
    assert (work / "docs" / "HANDOVER.md").read_text(encoding="utf-8") == (
        "uncommitted local edits\n"
    )

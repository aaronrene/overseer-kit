"""Data-integrity tier §PLS.10 — dirty bytes untouched; clean sync matches origin; ff-only."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.support import gh_merged_runner, pls_config
from tools.close_ritual.pr_land import run_pr_land


def _git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


@pytest.fixture
def land_repos(tmp_path: Path) -> tuple[Path, Path]:
    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare", "-b", "main")

    work = tmp_path / "work"
    _git(tmp_path, "clone", str(origin), "work")
    _git(work, "config", "user.email", "test@example.com")
    _git(work, "config", "user.name", "test")
    (work / "tracked.md").write_text("v1\n", encoding="utf-8")
    (work / ".gitignore").write_text(".overseer/\n", encoding="utf-8")
    _git(work, "add", ".")
    _git(work, "commit", "-m", "seed")
    _git(work, "push", "-u", "origin", "main")

    other = tmp_path / "other"
    _git(tmp_path, "clone", str(origin), "other")
    _git(other, "config", "user.email", "test@example.com")
    _git(other, "config", "user.name", "test")
    (other / "tracked.md").write_text("v2 landed\n", encoding="utf-8")
    _git(other, "add", ".")
    _git(other, "commit", "-m", "landed PR")
    _git(other, "push", "origin", "main")

    (work / ".overseer").mkdir()
    return work, origin


def test_dirty_unique_bytes_unchanged_after_skipped_sync(
    land_repos: tuple[Path, Path],
) -> None:
    work, _origin = land_repos
    unique = "UNIQUE-LOCAL-CONTENT-9c2f\n"
    (work / "tracked.md").write_text(unique, encoding="utf-8")

    result = run_pr_land(
        "3",
        authorization="operator: integrity dirty",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=work,
        config=pls_config(work),
    )

    assert result.post_land_sync["status"] == "skipped_dirty"
    assert (work / "tracked.md").read_text(encoding="utf-8") == unique


def test_clean_sync_bytes_equal_origin_main_no_invented_commits(
    land_repos: tuple[Path, Path],
) -> None:
    work, _origin = land_repos
    origin_tip = _git(work, "ls-remote", "origin", "main").split()[0]

    result = run_pr_land(
        "3",
        authorization="operator: integrity clean",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=work,
        config=pls_config(work),
    )

    assert result.post_land_sync["status"] == "synced"
    # Working-tree bytes for a tracked file equal origin/main after pull.
    assert (work / "tracked.md").read_text(encoding="utf-8") == "v2 landed\n"
    # ff-only: local main is exactly the origin tip — no merge/invented commits.
    assert _git(work, "rev-parse", "main") == origin_tip
    assert _git(work, "rev-parse", "main") == _git(work, "rev-parse", "origin/main")

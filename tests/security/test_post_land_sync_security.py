"""Security tier §PLS.10 — no force/clobber argv, muse-only zero argv, fail-closed refs."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import FakeGitRunner, gh_merged_runner, pls_config
from tools.close_ritual.pr_land import run_pr_land
from tools.close_ritual.post_land_sync import run_post_land_sync

KIT_ROOT = Path(__file__).resolve().parent.parent.parent

FORBIDDEN_FRAGMENTS = ("--force", "reset", "--hard", "clean", "-fd", "--auto", "stash")


@pytest.mark.parametrize(
    "porcelain, branch",
    [
        ("", "main"),
        ("", "feat/pls-sec"),
        (" M dirty.md\n", "main"),
        (" M dirty.md\n", "feat/pls-sec"),
    ],
)
def test_call_log_never_contains_force_or_clobber(
    repo_root: Path, porcelain: str, branch: str
) -> None:
    git = FakeGitRunner(porcelain=porcelain, branch=branch)
    run_post_land_sync(
        repo_root=repo_root,
        regime="git-only",
        remote="origin",
        main_branch="main",
        git_runner=git,
    )
    for call in git.calls:
        for fragment in FORBIDDEN_FRAGMENTS:
            assert fragment not in call, f"forbidden {fragment!r} in {call}"


def test_muse_only_fixture_zero_git_and_gh_argv_from_sync(repo_root: Path) -> None:
    git = FakeGitRunner()
    gh_calls: list[list[str]] = []
    gh = gh_merged_runner()

    def recording_gh(cmd: list[str]):
        gh_calls.append(list(cmd))
        return gh(cmd)

    result = run_pr_land(
        "5",
        authorization="operator: muse-only security",
        runner=recording_gh,
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root, "config-muse-only.yaml"),
        git_runner=git,
    )
    assert result.post_land_sync["status"] == "regime_skipped"
    assert git.calls == []
    # gh argv comes only from the merge path itself, never from the sync helper.
    assert all(call[:2] in (["gh", "pr"],) for call in gh_calls)
    merge_calls = [c for c in gh_calls if c[:3] == ["gh", "pr", "merge"]]
    assert all("--auto" not in c for c in merge_calls)


@pytest.mark.parametrize(
    "remote, main_branch",
    [
        ("--upload-pack=/tmp/evil", "main"),
        ("origin", "--force"),
        ("origin", "main branch"),
        ("origin\n", "main"),
        ("", "main"),
        ("origin", ""),
    ],
)
def test_metacharacter_refs_fail_closed_with_zero_git_argv(
    repo_root: Path, remote: str, main_branch: str
) -> None:
    git = FakeGitRunner()
    report = run_post_land_sync(
        repo_root=repo_root,
        regime="git-only",
        remote=remote,
        main_branch=main_branch,
        git_runner=git,
    )
    assert report.status == "failed"
    assert git.calls == []


def test_refuse_blind_auto_merge_policy_still_holds(repo_root: Path) -> None:
    tiers = (KIT_ROOT / "policy" / "tiers.yaml").read_text(encoding="utf-8")
    assert "refuse_blind_auto_merge: true" in tiers
    # PrLandResult.auto_merge stays False even through a synced land.
    result = run_pr_land(
        "5",
        authorization="operator: policy check",
        runner=gh_merged_runner(),
        sleep_fn=lambda _s: None,
        repo_root=repo_root,
        config=pls_config(repo_root),
        git_runner=FakeGitRunner(branch="main"),
    )
    assert result.auto_merge is False

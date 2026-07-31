"""Integration: injected-runner ``--write`` through §GSB C0 reconcile (§GSB.8).

Fixture 1 (per regime): existing ``feat/governance-sync-<today>`` behind
``T_target`` → FF then successful ensure, plan/push under the original dated
name. Fixture 2: diverged tip → uniquified ``-2`` used for commit / push /
``pr_url``. Fixture 3 (``muse+git-mirror``): Muse HEAD already stranded on
the stale dated branch while Git HEAD is on advanced main → C0 still
reconciles both histories so C1 does not exit ``2``.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_git_only_existing_branch_behind_ff_then_ensure(tmp_path: Path) -> None:
    branch = _feature_branch()
    handover_path, _ = seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(
        tmp_path,
        "git-only",
        existing_git_branches={branch},
        git_tips={branch: "stale1"},  # main defaults to feedface
        git_ancestors={"feedface": {"stale1"}},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.git_branch == branch
    # FF happened via an ancestor-validated tip move, then one sync commit.
    assert any(c.startswith("git branch -f ") for c, _ in runner.calls)
    assert runner.git_commit_count == 1
    tip = runner.git_tips[branch]
    assert "feedface" in runner.git_ancestors[tip]
    # Push targets the original dated name — no uniquify on the FF path.
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(branch in c and f"{branch}-" not in c for c in push_calls)
    assert not any(c.startswith("muse") for c, _ in runner.calls)
    assert "cafebabe" in handover_path.read_text(encoding="utf-8")


def test_muse_only_existing_branch_behind_ff_then_ensure(tmp_path: Path) -> None:
    branch = _feature_branch()
    handover_path, _ = seed_gsw_repo(tmp_path, "muse-only")
    original = handover_path.read_text(encoding="utf-8")
    runner = gsw_runner(
        tmp_path,
        "muse-only",
        existing_muse_branches={branch},
        muse_tips={branch: "sha256:stale"},  # main defaults to sha256:musetip
        muse_ancestors={"sha256:musetip": {"sha256:stale"}},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.muse_branch == branch
    assert any(
        c.startswith("muse") and f" update-ref {branch} sha256:musetip" in c
        for c, _ in runner.calls
    )
    assert runner.muse_commit_count == 1
    tip = runner.muse_tips[branch]
    assert "sha256:musetip" in runner.muse_ancestors[tip]
    assert handover_path.read_text(encoding="utf-8") != original
    # §GSB.8 least privilege: muse-only never invokes git/gh.
    assert not any(c.startswith(("git ", "gh ")) for c, _ in runner.calls)


def test_muse_git_mirror_existing_branch_behind_ff_both_histories(tmp_path: Path) -> None:
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    runner = gsw_runner(
        tmp_path,
        "muse+git-mirror",
        existing_git_branches={branch},
        existing_muse_branches={branch},
        git_tips={branch: "gitstale"},
        muse_tips={branch: "sha256:stale"},
        git_ancestors={"feedface": {"gitstale"}},
        muse_ancestors={"sha256:musetip": {"sha256:stale"}},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.git_branch == branch
    assert runner.muse_branch == branch
    assert any(c.startswith("git branch -f ") for c, _ in runner.calls)
    assert any(c.startswith("muse") and " update-ref " in c for c, _ in runner.calls)
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(branch in c for c in push_calls)
    assert not any("--force" in c for c, _ in runner.calls)


def test_diverged_tip_uniquifies_commit_push_and_pr_url(tmp_path: Path) -> None:
    """Fixture 2: a diverged same-day branch keeps its tip; commit/push/pr_url
    all use the deterministic ``-2`` name (frozen-plan replace)."""
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    runner = gsw_runner(
        tmp_path,
        "muse+git-mirror",
        existing_git_branches={branch},
        existing_muse_branches={branch},
        # Muse side diverged; git side behind — cross-history rule → uniquify.
        git_tips={branch: "gitstale"},
        muse_tips={branch: "sha256:divergent"},
        git_ancestors={"feedface": {"gitstale"}},
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
    assert code == 0
    uniquified = f"{branch}-2"
    assert runner.git_branch == uniquified
    assert runner.muse_branch == uniquified
    # Diverged original tips untouched (no partial FF, no rewind).
    assert runner.git_tips[branch] == "gitstale"
    assert runner.muse_tips[branch] == "sha256:divergent"
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(uniquified in c for c in push_calls)
    assert f"main...{uniquified}?expand=1" in buf.getvalue()


def test_mirror_muse_head_stranded_on_stale_branch_reconciles(tmp_path: Path) -> None:
    """Fixture 3 (R1-M2): Muse HEAD already on the stale dated branch while
    Git HEAD is on advanced main — T_target falls back to configured main on
    the Muse side, C0 fast-forwards both histories, and C1 succeeds."""
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    runner = gsw_runner(
        tmp_path,
        "muse+git-mirror",
        muse_branch=branch,
        # Session work in progress on the shared tree — also keeps the KH2
        # muse-sync gate (muse-dirty + git-clean → pending) out of the way so
        # the reconcile path itself is what's under test.
        git_dirty=True,
        existing_git_branches={branch},
        existing_muse_branches={"main"},
        git_tips={branch: "gitstale"},
        muse_tips={branch: "sha256:stale", "main": "sha256:musetip"},
        git_ancestors={"feedface": {"gitstale"}},
        muse_ancestors={"sha256:musetip": {"sha256:stale"}},
        # Shared worktree holds the advanced-main bytes; the stale tips hold
        # distinct day-1 content (the live PLS land-b shape).
        content_map={
            "sha256:stale": "content:day1-muse",
            "gitstale": "content:day1-git",
        },
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.git_branch == branch
    assert runner.muse_branch == branch
    # Muse FF used update-ref against configured main — not HEAD-equal skip.
    assert any(
        c.startswith("muse") and f" update-ref {branch} sha256:musetip" in c
        for c, _ in runner.calls
    )
    assert any(c.startswith("git branch -f ") for c, _ in runner.calls)
    # The Git checkout was never refused by leftover stale bytes.
    assert not any("--force" in c for c, _ in runner.calls)
    assert runner.muse_commit_count == 1

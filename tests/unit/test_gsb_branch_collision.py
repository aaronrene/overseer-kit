"""Unit tests for §GSB C0 reconcile-before-ensure (§GSB.8 unit tier).

Covers the seven frozen unit cases: (1) ancestor/equal → FF vs non-ancestor
→ uniquify classification, (2) ``O_H == B`` → ``T_target`` from configured
main, (3) deterministic lowest free ``-N`` uniquify, (4) FF via tip update
without checkout-as-FF, (5) cross-history diverged side → uniquify with no
partial FF, (6) equal tips never uniquify, (7) frozen ``PatchPlan`` replaced
so commit/push/``pr_url`` observe the reconciled name.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    BranchStateRunner,
    adapter_for,
    gsw_runner,
    run_cli,
    seed_gsw_repo,
)
from tools.governance_hygiene.engine import (
    BranchState,
    _classify_git_branch,
    _classify_muse_branch,
    _reconcile_feature_branch,
    _uniquify_branch,
)


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_git_classifier_ancestor_equal_and_diverged(git_only_config, repo_root) -> None:
    """§GSB.3.2 case 1: T_exist ancestor-of / equal-to T_target → FF class;
    non-ancestor → uniquify class."""
    branch = _feature_branch()

    # Behind (ancestor): stale tip is an ancestor of main's tip.
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={branch},
        git_tips={branch: "stale1", "main": "tip2"},
        git_ancestors={"tip2": {"stale1"}},
    )
    probe, error = _classify_git_branch(runner, repo_root, git_only_config, branch, "main")
    assert error is None
    assert probe is not None and probe.exists and probe.ancestor
    assert probe.tip == "stale1" and probe.target == "tip2"

    # Equal tips classify as ancestor (§GSB.3.3 equal-tips rule).
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={branch},
        git_tips={branch: "tip2", "main": "tip2"},
    )
    probe, error = _classify_git_branch(runner, repo_root, git_only_config, branch, "main")
    assert error is None
    assert probe is not None and probe.ancestor

    # Diverged (both commits known, no ancestry edge) → uniquify class.
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={branch},
        git_tips={branch: "divergent", "main": "tip2"},
    )
    probe, error = _classify_git_branch(runner, repo_root, git_only_config, branch, "main")
    assert error is None
    assert probe is not None and probe.exists and not probe.ancestor


def test_target_resolves_to_configured_main_when_head_on_dated_branch(
    git_only_config, muse_git_mirror_config, repo_root
) -> None:
    """§GSB.3.2.1 case 2: O_H == B must not use HEAD as T_target — the
    configured main is the reconcile base ref on both histories."""
    branch = _feature_branch()

    runner = BranchStateRunner(
        str(repo_root),
        git_branch=branch,
        existing_git_branches={"main"},
        git_tips={branch: "stale1", "main": "tip2"},
        git_ancestors={"tip2": {"stale1"}},
    )
    probe, error = _classify_git_branch(runner, repo_root, git_only_config, branch, branch)
    assert error is None
    assert probe is not None and probe.target == "tip2" and probe.ancestor
    assert any(c == "git rev-parse main" for c, _ in runner.calls)

    runner = BranchStateRunner(
        str(repo_root),
        muse_branch=branch,
        existing_muse_branches={"main"},
        muse_tips={branch: "sha256:stale", "main": "sha256:tip2"},
        muse_ancestors={"sha256:tip2": {"sha256:stale"}},
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    probe, error = _classify_muse_branch(
        adapter, runner, repo_root, muse_git_mirror_config, branch, branch
    )
    assert error is None
    assert probe is not None and probe.target == "sha256:tip2" and probe.ancestor
    assert any(c.endswith("rev-parse main") for c, _ in runner.calls if c.startswith("muse"))


def test_uniquify_picks_lowest_free_suffix_deterministically(
    muse_git_mirror_config, repo_root
) -> None:
    """§GSB.3.3 case 3: lowest N≥2 free on ALL applicable histories; same
    inputs → same suffix across runs."""
    branch = _feature_branch()

    def build() -> BranchStateRunner:
        # -2 taken on git only, -3 taken on muse only → -4 is the lowest
        # candidate free everywhere.
        return BranchStateRunner(
            str(repo_root),
            existing_git_branches={branch, f"{branch}-2"},
            existing_muse_branches={branch, f"{branch}-3"},
        )

    first = build()
    adapter = adapter_for(muse_git_mirror_config, repo_root, first)
    name_one, error = _uniquify_branch(
        adapter, first, repo_root, muse_git_mirror_config, branch
    )
    assert error is None
    assert name_one == f"{branch}-4"

    second = build()
    adapter = adapter_for(muse_git_mirror_config, repo_root, second)
    name_two, error = _uniquify_branch(
        adapter, second, repo_root, muse_git_mirror_config, branch
    )
    assert error is None
    assert name_two == name_one


def test_ff_uses_tip_update_never_checkout_of_dated_branch(
    muse_git_mirror_config, repo_root
) -> None:
    """§GSB.3.3 case 4: FF path moves tips via allowed forms (update-ref /
    branch -f / muse -C copy) — never a checkout of B as the FF mechanism."""
    branch = _feature_branch()
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={branch},
        existing_muse_branches={branch},
        git_tips={branch: "gitstale", "main": "tip2"},
        muse_tips={branch: "sha256:stale", "main": "sha256:tip2"},
        git_ancestors={"tip2": {"gitstale"}},
        muse_ancestors={"sha256:tip2": {"sha256:stale"}},
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    state = BranchState(git_branch="main", muse_branch="main")
    reconciled, error = _reconcile_feature_branch(
        adapter, runner, repo_root, muse_git_mirror_config, branch, state
    )
    assert error is None
    assert reconciled == branch
    assert runner.git_tips[branch] == "tip2"
    assert runner.muse_tips[branch] == "sha256:tip2"
    commands = [c for c, _ in runner.calls]
    assert any(c.startswith("muse") and " update-ref " in c for c in commands)
    assert any(c.startswith("git branch -f ") for c in commands)
    # C0 spy rule: no Muse or Git checkout at all during reconcile.
    assert not any("checkout" in c for c in commands)
    assert not any("--force" in c for c in commands)


def test_cross_history_divergence_uniquifies_without_partial_ff(
    muse_git_mirror_config, repo_root
) -> None:
    """§GSB.3.2 case 5: one side diverged → uniquify the shared name; the
    ancestor side must NOT be fast-forwarded under the original name."""
    branch = _feature_branch()
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={branch},
        existing_muse_branches={branch},
        # Git side is a clean ancestor; Muse side diverged (no ancestry edge).
        git_tips={branch: "gitstale", "main": "tip2"},
        muse_tips={branch: "sha256:divergent", "main": "sha256:tip2"},
        git_ancestors={"tip2": {"gitstale"}},
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    state = BranchState(git_branch="main", muse_branch="main")
    reconciled, error = _reconcile_feature_branch(
        adapter, runner, repo_root, muse_git_mirror_config, branch, state
    )
    assert error is None
    assert reconciled == f"{branch}-2"
    # No partial FF: both existing tips untouched.
    assert runner.git_tips[branch] == "gitstale"
    assert runner.muse_tips[branch] == "sha256:divergent"
    commands = [c for c, _ in runner.calls]
    assert not any(" update-ref " in c for c in commands)
    assert not any(c.startswith("git branch -f ") for c in commands)


def test_equal_tips_never_uniquify(muse_git_mirror_config, repo_root) -> None:
    """§GSB.3.3 case 6: equal tips are the ancestor class — a no-op FF, and
    never a reason to uniquify."""
    branch = _feature_branch()
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={branch},
        existing_muse_branches={branch},
        git_tips={branch: "tip2", "main": "tip2"},
        muse_tips={branch: "sha256:tip2", "main": "sha256:tip2"},
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    state = BranchState(git_branch="main", muse_branch="main")
    reconciled, error = _reconcile_feature_branch(
        adapter, runner, repo_root, muse_git_mirror_config, branch, state
    )
    assert error is None
    assert reconciled == branch
    commands = [c for c, _ in runner.calls]
    assert not any(" update-ref " in c for c in commands)
    assert not any(c.startswith("git branch -f ") for c in commands)
    assert not any("checkout" in c for c in commands)


def test_uniquify_replaces_frozen_plan_branch_and_pr_url(tmp_path: Path) -> None:
    """§GSB.3.3 case 7 (R1-M1/R1-M5): the frozen PatchPlan is replaced so the
    success-path commit, push, and pr_url all observe the uniquified name."""
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(
        tmp_path,
        "git-only",
        existing_git_branches={branch},
        # Diverged: both tips known to the graph, no ancestry edge.
        git_tips={branch: "divergent", "main": "feedface"},
    )

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
    assert code == 0
    uniquified = f"{branch}-2"
    assert runner.git_branch == uniquified
    # Original diverged branch untouched; new commit landed on the -2 name.
    assert runner.git_tips[branch] == "divergent"
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(uniquified in c for c in push_calls)
    output = buf.getvalue()
    assert f"governance-sync branch uniquified: {uniquified}" in output
    assert f"main...{uniquified}?expand=1" in output

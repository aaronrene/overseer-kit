"""Security tests for §GSB C0 reconcile (§GSB.8 security tier).

(1) Shell-metacharacter branch names stay quoted data through the reconcile
probes, tip updates, and uniquify; (2) ``git-only`` collision runs zero muse
argv; (3) ``muse-only`` collision runs zero git/gh argv; (4) no ``checkout
--force`` in the default FF / uniquify / ensure / rollback paths — the
ancestor-validated tip moves remain allowed.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from adapters.runner import quote_arg
from cli.kit_root import kit_root
from tests.support import (
    BranchStateRunner,
    adapter_for,
    gsw_runner,
    run_cli,
    seed_gsw_repo,
)
from tools.governance_hygiene.engine import BranchState, _reconcile_feature_branch

HOSTILE_BRANCH = "feat/x; touch /tmp/pwned $(id)"


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_hostile_branch_name_stays_quoted_through_reconcile(
    git_only_config, repo_root
) -> None:
    """Branch names from config patterns are data — quoted argv in every
    reconcile probe and tip update, never interpolated."""
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={HOSTILE_BRANCH},
        git_tips={HOSTILE_BRANCH: "stale1", "main": "tip2"},
        git_ancestors={"tip2": {"stale1"}},
    )
    adapter = adapter_for(git_only_config, repo_root, runner)
    state = BranchState(git_branch="main", muse_branch=None)
    reconciled, error = _reconcile_feature_branch(
        adapter, runner, repo_root, git_only_config, HOSTILE_BRANCH, state
    )
    assert error is None
    assert reconciled == HOSTILE_BRANCH
    assert runner.git_tips[HOSTILE_BRANCH] == "tip2"
    touched = [c for c, _ in runner.calls if "feat/x" in c]
    assert touched
    for command in touched:
        # The metacharacters never appear outside a quoted argument.
        stripped = command.replace(quote_arg(HOSTILE_BRANCH), "").replace(
            quote_arg("refs/heads/" + HOSTILE_BRANCH), ""
        )
        assert "; touch" not in stripped
        assert "$(id)" not in stripped


def test_hostile_branch_name_stays_quoted_through_uniquify(
    git_only_config, repo_root
) -> None:
    runner = BranchStateRunner(
        str(repo_root),
        existing_git_branches={HOSTILE_BRANCH},
        git_tips={HOSTILE_BRANCH: "divergent", "main": "tip2"},
    )
    adapter = adapter_for(git_only_config, repo_root, runner)
    state = BranchState(git_branch="main", muse_branch=None)
    reconciled, error = _reconcile_feature_branch(
        adapter, runner, repo_root, git_only_config, HOSTILE_BRANCH, state
    )
    assert error is None
    assert reconciled == f"{HOSTILE_BRANCH}-2"
    for command, _ in runner.calls:
        if "feat/x" not in command:
            continue
        stripped = command
        for name in (reconciled, HOSTILE_BRANCH):
            stripped = stripped.replace(quote_arg("refs/heads/" + name), "").replace(
                quote_arg(name), ""
            )
        assert "; touch" not in stripped
        assert "$(id)" not in stripped


def test_git_only_collision_write_zero_muse_argv(tmp_path: Path) -> None:
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(
        tmp_path,
        "git-only",
        existing_git_branches={branch},
        git_tips={branch: "stale1"},
        git_ancestors={"feedface": {"stale1"}},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert not any(c.startswith("muse") for c, _ in runner.calls)


def test_muse_only_collision_write_zero_git_argv(tmp_path: Path) -> None:
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "muse-only")
    runner = gsw_runner(
        tmp_path,
        "muse-only",
        existing_muse_branches={branch},
        muse_tips={branch: "sha256:stale"},
        muse_ancestors={"sha256:musetip": {"sha256:stale"}},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert not any(c.startswith(("git ", "gh ")) for c, _ in runner.calls)


def test_no_checkout_force_in_ff_uniquify_ensure_or_rollback(tmp_path: Path) -> None:
    """§GSB.6: --force never appears — FF success, uniquify success, and the
    rollback path after an induced commit failure all stay force-free."""
    branch = _feature_branch()

    # FF success path.
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    ff_runner = gsw_runner(
        tmp_path,
        "muse+git-mirror",
        existing_git_branches={branch},
        existing_muse_branches={branch},
        git_tips={branch: "gitstale"},
        muse_tips={branch: "sha256:stale"},
        git_ancestors={"feedface": {"gitstale"}},
        muse_ancestors={"sha256:musetip": {"sha256:stale"}},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=ff_runner, kit=kit_root())
    assert code == 0
    assert not any("--force" in c for c, _ in ff_runner.calls)

    # Uniquify success path.
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    uniq_runner = gsw_runner(
        tmp_path,
        "muse+git-mirror",
        existing_git_branches={branch},
        existing_muse_branches={branch},
        git_tips={branch: "divergent-git"},
        muse_tips={branch: "sha256:divergent"},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=uniq_runner, kit=kit_root())
    assert code == 0
    assert uniq_runner.git_branch == f"{branch}-2"
    assert not any("--force" in c for c, _ in uniq_runner.calls)

    # Rollback path after induced commit failure with a collision present.
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    failing = gsw_runner(
        tmp_path,
        "muse+git-mirror",
        muse_commit_fails=True,
        existing_git_branches={branch},
        existing_muse_branches={branch},
        git_tips={branch: "gitstale"},
        muse_tips={branch: "sha256:stale"},
        git_ancestors={"feedface": {"gitstale"}},
        muse_ancestors={"sha256:musetip": {"sha256:stale"}},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=failing, kit=kit_root())
    assert code == 2
    assert failing.git_branch == "main" and failing.muse_branch == "main"
    assert not any("--force" in c for c, _ in failing.calls)

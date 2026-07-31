"""Security tests for the §GSW write path (§GSW.10 security tier).

(1) Shell-metacharacter branch names stay quoted data; (2) git-only never
invokes muse; (3) muse-only never invokes git/gh; (4) no ``--force``
checkout in default success or rollback paths.
"""

from __future__ import annotations

from pathlib import Path

from adapters.runner import quote_arg
from cli.kit_root import kit_root
from tests.support import adapter_for, gsw_runner, make_runner, ok, run_cli, seed_gsw_repo
from tools.governance_hygiene.engine import (
    BranchState,
    _ensure_feature_branch,
    _restore_branch_state,
)

HOSTILE_BRANCH = "feat/x; touch /tmp/pwned $(id)"


def test_hostile_branch_name_is_quoted_in_ensure(git_only_config, repo_root) -> None:
    """Branch names from config patterns are data — quoted argv, never interpolated."""
    runner = make_runner({"git checkout": ok("")})
    adapter = adapter_for(git_only_config, repo_root, runner)
    state = BranchState(git_branch="main", muse_branch=None)
    error = _ensure_feature_branch(
        adapter, runner, repo_root, git_only_config, HOSTILE_BRANCH, state
    )
    assert error is None
    checkout_calls = [c for c, _ in runner.calls if "checkout" in c]
    assert checkout_calls
    for command in checkout_calls:
        assert quote_arg(HOSTILE_BRANCH) in command
        # The metacharacters never appear outside the quoted argument.
        assert "; touch" not in command.replace(quote_arg(HOSTILE_BRANCH), "")


def test_hostile_branch_name_is_quoted_in_muse_ensure_and_restore(
    muse_only_config, repo_root
) -> None:
    root = str(repo_root)
    runner = make_runner({f"muse -C {root} checkout": ok(""), f"muse -C {root} rev-parse": ok("main")})
    adapter = adapter_for(muse_only_config, repo_root, runner)
    state = BranchState(git_branch=None, muse_branch="main")
    error = _ensure_feature_branch(
        adapter, runner, repo_root, muse_only_config, HOSTILE_BRANCH, state
    )
    assert error is None
    hostile_state = BranchState(git_branch=None, muse_branch=HOSTILE_BRANCH)
    _restore_branch_state(muse_only_config, adapter, runner, repo_root, hostile_state)
    checkout_calls = [c for c, _ in runner.calls if "checkout" in c]
    assert checkout_calls
    for command in checkout_calls:
        assert quote_arg(HOSTILE_BRANCH) in command
        assert "; touch" not in command.replace(quote_arg(HOSTILE_BRANCH), "")


def test_git_only_write_call_log_has_zero_muse_argv(tmp_path: Path) -> None:
    seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(tmp_path, "git-only", git_dirty=True)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert not any(c.startswith("muse") for c, _ in runner.calls)


def test_muse_only_write_call_log_has_zero_git_argv(tmp_path: Path) -> None:
    seed_gsw_repo(tmp_path, "muse-only")
    runner = gsw_runner(tmp_path, "muse-only", muse_dirty=True)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert not any(c.startswith(("git ", "gh ")) for c, _ in runner.calls)


def test_no_force_checkout_in_success_or_rollback_paths(tmp_path: Path) -> None:
    """§GSW.4.3 / §GSW.6.2: --force is forbidden as default in both directions."""
    seed_gsw_repo(tmp_path, "muse+git-mirror")

    # Success path with dirty tree on both histories.
    success = gsw_runner(tmp_path, "muse+git-mirror", git_dirty=True, muse_dirty=True)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=success, kit=kit_root())
    assert code == 0
    assert not any("--force" in c for c, _ in success.calls)

    # Rollback path after induced commit failure.
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    failing = gsw_runner(tmp_path, "muse+git-mirror", muse_commit_fails=True)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=failing, kit=kit_root())
    assert code == 2
    assert failing.git_branch == "main" and failing.muse_branch == "main"
    assert not any("--force" in c for c, _ in failing.calls)

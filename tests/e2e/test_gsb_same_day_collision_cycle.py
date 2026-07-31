"""E2E: same-day-collision ``--write`` on ALL three regimes (§GSB.8 e2e).

The frozen coverage-gap close for the live 2026-07-31 PLS land-b defect:
the first ``--write`` creates the dated sync branch + commit; a second
``--write`` on the same calendar day — after the original branch's tip
advanced (post-land main) — must succeed without exit ``2``. Under
``muse+git-mirror`` the Git worktree must never be left in a state that
refuses checkout after the Muse ensure; ``main`` stays untouched;
``muse-only`` runs zero git argv and ``git-only`` zero muse argv.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_git_only_same_day_second_write_succeeds(tmp_path: Path) -> None:
    branch = _feature_branch()
    handover_path, _ = seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(tmp_path, "git-only")

    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.git_branch == branch
    first_tip = runner.git_tips[branch]

    # Simulate the land + post-land posture: the sync branch merged, main
    # advanced past it, operator back on main; GitHub main moved (D1 drift).
    runner.git_branch = "main"
    runner.git_tips["main"] = "postland"
    runner.git_ancestors["postland"] = {first_tip} | runner.git_ancestors.get(
        first_tip, set()
    )
    runner.worktree = runner._content("postland")
    runner.origin_main_tip = "postland"

    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0, "same-day second --write must not exit 2"
    assert runner.git_branch == branch
    # FF then exactly one new sync commit on top of the post-land tip.
    second_tip = runner.git_tips[branch]
    assert second_tip != first_tip
    assert "postland" in runner.git_ancestors[second_tip]
    # main untouched by the reconcile.
    assert runner.git_tips["main"] == "postland"
    assert "postland" in handover_path.read_text(encoding="utf-8")
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(branch in c for c in push_calls)
    assert not any(c.startswith("muse") for c, _ in runner.calls)
    assert not any("--force" in c for c, _ in runner.calls)


def test_muse_only_same_day_second_write_zero_git_argv(tmp_path: Path) -> None:
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "muse-only")
    runner = gsw_runner(tmp_path, "muse-only")

    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.muse_branch == branch
    first_tip = runner.muse_tips[branch]

    # Post-land: muse main advanced past the day-1 sync commit; operator back
    # on main; fresh D2 drift drives the second apply.
    runner.muse_branch = "main"
    runner.muse_tips["main"] = "sha256:postland"
    runner.muse_ancestors["sha256:postland"] = {first_tip} | runner.muse_ancestors.get(
        first_tip, set()
    )
    runner.worktree = runner._content("sha256:postland")
    runner.muse_rev_parse_main_values = ["sha256:anchor2", "sha256:moved2"]

    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0, "same-day second --write must not exit 2"
    assert runner.muse_branch == branch
    second_tip = runner.muse_tips[branch]
    assert second_tip != first_tip
    assert "sha256:postland" in runner.muse_ancestors[second_tip]
    assert runner.muse_tips["main"] == "sha256:postland"
    # §GSB.8 least privilege across BOTH runs: zero git/gh argv.
    assert not any(c.startswith(("git ", "gh ")) for c, _ in runner.calls)
    assert not any("--force" in c for c, _ in runner.calls)


def test_muse_git_mirror_same_day_second_write_never_refuses_checkout(
    tmp_path: Path,
) -> None:
    """The live defect class: after the first sync, the dated branch tips are
    stale day-1 content on both histories. The second same-day ``--write``
    must reconcile them so the Muse ensure never rewrites the shared worktree
    to a stale tip that makes the Git checkout refuse."""
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "muse+git-mirror")
    runner = gsw_runner(tmp_path, "muse+git-mirror")

    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.git_branch == branch and runner.muse_branch == branch
    muse_tip_one = runner.muse_tips[branch]
    git_tip_one = runner.git_tips[branch]

    # Post-land: both mains advanced past the day-1 sync; operator back on
    # main on both histories; bridge anchor follows muse main (D2 aligned);
    # GitHub main moved (D1 drift drives the apply). The day-1 tips hold
    # distinct content from the post-land tree — the exact live shape whose
    # stale checkout dirtied the Git tree.
    runner.git_branch = "main"
    runner.muse_branch = "main"
    runner.git_tips["main"] = "postland"
    runner.muse_tips["main"] = "sha256:postland"
    runner.git_ancestors["postland"] = {git_tip_one} | runner.git_ancestors.get(
        git_tip_one, set()
    )
    runner.muse_ancestors["sha256:postland"] = {muse_tip_one} | runner.muse_ancestors.get(
        muse_tip_one, set()
    )
    runner.origin_main_tip = "postland"
    runner.content_map[muse_tip_one] = "content:day1-muse"
    runner.content_map[git_tip_one] = "content:day1-git"
    runner.worktree = runner._content("postland")
    (tmp_path / ".muse" / "git-bridge.toml").write_text(
        f'[last_export]\nmuse_commit_id = "sha256:postland"\ngit_sha = "{"1" * 40}"\n',
        encoding="utf-8",
    )

    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0, "same-day second --write must not exit 2 (live defect class)"
    # Dual-HEAD success posture on the reconciled dated branch.
    assert runner.git_branch == branch
    assert runner.muse_branch == branch
    # The Git checkout was never refused: reconcile put the tips at the
    # post-land targets before any checkout of the dated name.
    refused = [
        c for c, _ in runner.calls if "would be overwritten by checkout" in c
    ]
    assert refused == []
    second_muse_tip = runner.muse_tips[branch]
    assert second_muse_tip != muse_tip_one
    assert "sha256:postland" in runner.muse_ancestors[second_muse_tip]
    # main untouched on both histories.
    assert runner.git_tips["main"] == "postland"
    assert runner.muse_tips["main"] == "sha256:postland"
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(branch in c for c in push_calls)
    assert not any(c.rstrip().endswith(" main") for c in push_calls)
    assert not any("--force" in c for c, _ in runner.calls)

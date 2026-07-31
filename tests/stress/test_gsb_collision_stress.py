"""Stress: repeated same-day ``--write`` with induced failure mid-C0 (§GSB.8).

N≥20 alternating attempts where the ensure fails after a partial C0 tip
update (Muse leg succeeded, Git leg fails — and the reverse): every failure
must restore ``original_branch_state`` on both histories, leave docs and
marker untouched, and never accumulate stranded HEADs on
``feat/governance-sync-*``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from adapters.runner import CommandResult
from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo

ROUNDS = 20


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_partial_c0_failure_never_strands_heads(tmp_path: Path) -> None:
    branch = _feature_branch()
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "muse+git-mirror")
    original_handover = handover_path.read_bytes()
    original_roadmap = roadmap_path.read_bytes()

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

    fail_muse_leg = False
    original_run = runner.run

    def breaking_run(command: str, *, cwd: str | None = None) -> CommandResult:
        if fail_muse_leg and command.startswith("muse") and " update-ref " in command:
            runner.calls.append((command, cwd))
            return CommandResult(stdout="", stderr="induced muse tip failure", exit_code=1)
        if not fail_muse_leg and command.startswith("git branch -f "):
            # Partial C0: the Muse leg already fast-forwarded before this.
            runner.calls.append((command, cwd))
            return CommandResult(stdout="", stderr="induced git tip failure", exit_code=1)
        return original_run(command, cwd=cwd)

    runner.run = breaking_run  # type: ignore[method-assign]

    for round_index in range(ROUNDS):
        fail_muse_leg = round_index % 2 == 1
        # Re-strand the stale tips so both C0 legs stay active every round.
        runner.git_tips[branch] = "gitstale"
        runner.muse_tips[branch] = "sha256:stale"

        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
        assert code == 2, f"round {round_index}: expected exit 2 on induced C0 failure"
        # §GSW.4.2 dual restore: no stranded HEAD on the dated sync branch.
        assert runner.git_branch == "main", f"round {round_index}: stranded git HEAD"
        assert runner.muse_branch == "main", f"round {round_index}: stranded muse HEAD"
        assert handover_path.read_bytes() == original_handover
        assert roadmap_path.read_bytes() == original_roadmap
        assert not (tmp_path / ".overseer" / "last_governance_sync").exists()

    # No uniquified strand accumulation either: only the seeded dated branch
    # plus main exist on each history.
    assert {b for b in runner.git_branches if b.startswith("feat/governance-sync-")} == {branch}
    assert {b for b in runner.muse_branches if b.startswith("feat/governance-sync-")} == {branch}
    assert not any("--force" in c for c, _ in runner.calls)

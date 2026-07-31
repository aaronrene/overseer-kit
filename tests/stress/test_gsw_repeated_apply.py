"""Stress: repeated apply with induced commit failure after branch switch (§GSW.10).

N≥20 failed applies per regime family: every failure must restore the
original branch — no strand accumulation of ``feat/governance-sync-*`` as
the current HEAD (the live 2026-07-31 defect).
"""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo

ROUNDS = 20


def test_repeated_commit_failure_never_strands_git_only(tmp_path: Path) -> None:
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "git-only")
    original_handover = handover_path.read_text(encoding="utf-8")
    original_roadmap = roadmap_path.read_text(encoding="utf-8")
    runner = gsw_runner(tmp_path, "git-only", git_commit_fails=True)

    for round_index in range(ROUNDS):
        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
        assert code == 2, f"round {round_index}: expected VCS failure exit 2"
        assert runner.git_branch == "main", f"round {round_index}: stranded git HEAD"
        assert handover_path.read_text(encoding="utf-8") == original_handover
        assert roadmap_path.read_text(encoding="utf-8") == original_roadmap
        assert not (tmp_path / ".overseer" / "last_governance_sync").exists()


def test_repeated_commit_failure_never_strands_muse_git_mirror(tmp_path: Path) -> None:
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "muse+git-mirror")
    original_handover = handover_path.read_text(encoding="utf-8")
    original_roadmap = roadmap_path.read_text(encoding="utf-8")
    runner = gsw_runner(tmp_path, "muse+git-mirror", muse_commit_fails=True)

    for round_index in range(ROUNDS):
        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
        assert code == 2, f"round {round_index}: expected VCS failure exit 2"
        # §GSW.4.2 dual restore: neither history left on the sync branch.
        assert runner.git_branch == "main", f"round {round_index}: stranded git HEAD"
        assert runner.muse_branch == "main", f"round {round_index}: stranded muse HEAD"
        assert handover_path.read_text(encoding="utf-8") == original_handover
        assert roadmap_path.read_text(encoding="utf-8") == original_roadmap
        assert not (tmp_path / ".overseer" / "last_governance_sync").exists()

    assert not any("--force" in c for c, _ in runner.calls)

"""Data-integrity: §GSB reconcile tip/doc/marker semantics (§GSB.8).

FF path: after success the feature-branch tip equals the pre-ensure current
tip plus exactly one new sync commit. Diverged path: the original diverged
branch tip is unchanged (never force-reset) and the uniquified branch holds
the new commit. Mid-C0 failure: doc bytes unchanged, marker unrestamped,
HEADs restored.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from adapters.runner import CommandResult
from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_ff_success_tip_is_target_plus_one_sync_commit(tmp_path: Path) -> None:
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
    # Exactly one commit, parented on the pre-ensure current tip (T_target).
    assert runner.git_commit_count == 1
    tip = runner.git_tips[branch]
    assert tip != "stale1" and tip != "feedface"
    # Parent chain: new sync commit → T_target ("feedface") → old stale tip.
    assert runner.git_ancestors[tip] == {"feedface", "stale1"}


def test_diverged_original_tip_unchanged_uniquified_holds_commit(tmp_path: Path) -> None:
    branch = _feature_branch()
    seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(
        tmp_path,
        "git-only",
        existing_git_branches={branch},
        git_tips={branch: "divergent"},
    )
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    uniquified = f"{branch}-2"
    # Original diverged tip untouched — never rewound or force-reset.
    assert runner.git_tips[branch] == "divergent"
    assert runner.git_commit_count == 1
    new_tip = runner.git_tips[uniquified]
    assert new_tip != "divergent"
    assert "feedface" in runner.git_ancestors[new_tip]
    assert not any("--force" in c for c, _ in runner.calls)
    assert not any(c.startswith("git branch -f ") for c, _ in runner.calls)


def test_mid_c0_failure_docs_marker_heads_untouched(tmp_path: Path) -> None:
    branch = _feature_branch()
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "muse+git-mirror")
    original_handover = handover_path.read_bytes()
    original_roadmap = roadmap_path.read_bytes()
    prior_marker = "2026-07-30T00:00:00Z\nr1=cafebabe\nr3=sha256:musetip\n"
    marker_path = tmp_path / ".overseer" / "last_governance_sync"
    marker_path.write_text(prior_marker, encoding="utf-8")

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
    original_run = runner.run

    def breaking_run(command: str, *, cwd: str | None = None) -> CommandResult:
        # Partial C0: muse update-ref succeeds, then the git leg fails.
        if command.startswith("git branch -f "):
            runner.calls.append((command, cwd))
            return CommandResult(stdout="", stderr="induced git tip failure", exit_code=1)
        return original_run(command, cwd=cwd)

    runner.run = breaking_run  # type: ignore[method-assign]
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 2
    # Zero doc writes before ensure success (§GSW order preserved by C0).
    assert handover_path.read_bytes() == original_handover
    assert roadmap_path.read_bytes() == original_roadmap
    # Marker unrestamped: prior bytes intact.
    assert marker_path.read_text(encoding="utf-8") == prior_marker
    # HEADs restored (they never moved during C0 tip probes/updates).
    assert runner.git_branch == "main"
    assert runner.muse_branch == "main"

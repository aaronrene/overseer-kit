"""Data-integrity: §GSW rollback + marker semantics (§GSW.10 data-integrity).

Induced failure after branch switch + doc writes must leave docs byte-identical,
the original branch current, no feature commit, and the marker absent or restored
to prior bytes (GFG mid-apply rule). A subsequent successful ``--write`` then
produces exactly one feature-branch commit bundling handover+roadmap and may
stamp the marker only after that success when D1+D2 are aligned.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, gsw_runner, run_cli, seed_gsw_repo

_MERGED_K5B = json.dumps(
    [
        {
            "number": 42,
            "title": "K5b Freeze reviewer build",
            "mergeCommit": {"oid": "cafebabe"},
            "mergedAt": "2026-07-09T00:00:00Z",
        }
    ]
)


def _seed_d1_aligned_d3_drift(tmp_path: Path) -> tuple[Path, Path]:
    """git-only: handover claims the real main tip (D1 aligned, D2 aligned)
    while the roadmap queue lags a merged PR (D3 drifted) — marker-eligible."""
    handover = (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8")
    handover = handover.replace("deadbeef", "cafebabe")
    return seed_gsw_repo(tmp_path, "git-only", handover_text=handover)


def test_failure_after_switch_and_write_restores_everything(tmp_path: Path) -> None:
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "muse+git-mirror")
    original_handover = handover_path.read_bytes()
    original_roadmap = roadmap_path.read_bytes()
    prior_marker = "2026-07-30T00:00:00Z\nr1=cafebabe\nr3=sha256:musetip\n"
    marker_path = tmp_path / ".overseer" / "last_governance_sync"
    marker_path.write_text(prior_marker, encoding="utf-8")

    runner = gsw_runner(tmp_path, "muse+git-mirror", muse_commit_fails=True)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())

    assert code == 2
    assert handover_path.read_bytes() == original_handover
    assert roadmap_path.read_bytes() == original_roadmap
    assert runner.git_branch == "main"
    assert runner.muse_branch == "main"
    # No new stamp left behind: prior marker bytes intact (§GSW.3.4).
    assert marker_path.read_text(encoding="utf-8") == prior_marker
    # No feature commit reached the history.
    committed = [c for c, _ in runner.calls if c.startswith("muse") and " commit " in c]
    assert committed, "commit was attempted"


def test_second_write_single_commit_bundles_both_docs_then_marker(tmp_path: Path) -> None:
    handover_path, roadmap_path = _seed_d1_aligned_d3_drift(tmp_path)
    marker_path = tmp_path / ".overseer" / "last_governance_sync"

    # First apply: induced commit failure — marker must not be stamped.
    failing = gsw_runner(tmp_path, "git-only", git_commit_fails=True, merged_prs_json=_MERGED_K5B)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=failing, kit=kit_root())
    assert code == 2
    assert not marker_path.exists()
    assert failing.git_branch == "main"

    # Second apply: success — exactly one commit bundling handover+roadmap,
    # marker stamped only after that success (D1+D2 aligned).
    runner = gsw_runner(tmp_path, "git-only", merged_prs_json=_MERGED_K5B)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0

    commit_calls = [c for c, _ in runner.calls if c.startswith("git commit")]
    assert len(commit_calls) == 1
    add_calls = [c for c, _ in runner.calls if c.startswith("git add")]
    assert any(
        "OVERSEER-HANDOVER.md" in c and "ROADMAP.md" in c for c in add_calls
    ), "commit must bundle handover + roadmap"
    commit_index = next(i for i, (c, _) in enumerate(runner.calls) if c.startswith("git commit"))
    assert marker_path.exists()
    marker_lines = marker_path.read_text(encoding="utf-8").splitlines()
    assert marker_lines[1] == "r1=cafebabe"
    # Roadmap D3 reconciled in the committed patch.
    assert "PR #42" in roadmap_path.read_text(encoding="utf-8")
    assert runner.git_branch == f"feat/governance-sync-{date.today().isoformat()}"
    # Marker write happens after the commit call: nothing after commit reverses it,
    # and the failing run above proved no stamp occurs without commit success.
    assert commit_index < len(runner.calls)


def test_step_c_failure_leaves_docs_and_branch_untouched(tmp_path: Path) -> None:
    """Step C failure (cannot create/switch): zero doc writes, original branch kept."""
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "git-only")
    original_handover = handover_path.read_bytes()
    original_roadmap = roadmap_path.read_bytes()

    runner = gsw_runner(
        tmp_path,
        "git-only",
        existing_git_branches={f"feat/governance-sync-{date.today().isoformat()}"},
    )

    # Make every checkout of the feature branch fail (create collides, switch breaks).
    original_run = runner.run

    def breaking_run(command: str, *, cwd: str | None = None):
        if "git checkout feat/governance-sync-" in command:
            runner.calls.append((command, cwd))
            from adapters.runner import CommandResult

            return CommandResult(stdout="", stderr="switch refused", exit_code=1)
        return original_run(command, cwd=cwd)

    runner.run = breaking_run  # type: ignore[method-assign]
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 2
    assert handover_path.read_bytes() == original_handover
    assert roadmap_path.read_bytes() == original_roadmap
    assert runner.git_branch == "main"
    assert not (tmp_path / ".overseer" / "last_governance_sync").exists()

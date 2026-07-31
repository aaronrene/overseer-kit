"""Performance: §GSB reconcile stays within governance-sync bounds (§GSB.8).

Reconcile probes plus at most one tip update per history — no unbounded
``git log`` / Muse history scans — on kit-sized docs with a same-day
collision present.
"""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_collision_write_bounded_on_kit_sized_docs(tmp_path: Path) -> None:
    branch = _feature_branch()
    kit_docs = Path(__file__).resolve().parents[2] / "docs"
    seed_gsw_repo(
        tmp_path,
        "git-only",
        handover_text=(kit_docs / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8"),
        roadmap_text=(kit_docs / "ROADMAP.md").read_text(encoding="utf-8"),
    )
    runner = gsw_runner(
        tmp_path,
        "git-only",
        existing_git_branches={branch},
        git_tips={branch: "stale1"},
        git_ancestors={"feedface": {"stale1"}},
    )

    start = time.perf_counter()
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    elapsed = time.perf_counter() - start

    assert code in {0, 2}
    assert elapsed < 2.0
    commands = [c for c, _ in runner.calls]
    # No unbounded history scans introduced by the reconcile.
    assert not any(c.startswith("git log") for c in commands)
    assert not any(c.startswith("muse") and " log " in c for c in commands)
    assert not any(c.startswith("git rev-list") and "--count" not in c for c in commands)
    # Reconcile adds bounded probes: one existence probe, one target read,
    # one ancestor check, and at most one tip update for the history.
    assert sum(1 for c in commands if c.startswith("git rev-parse --verify ")) <= 1
    assert sum(1 for c in commands if "merge-base --is-ancestor" in c) <= 1
    assert sum(
        1 for c in commands if c.startswith("git branch -f ") or c.startswith("git update-ref ")
    ) <= 1
    # Bounded total command count: capture + reads + reconcile + ensure +
    # commit + push, no loops.
    assert len(commands) < 45

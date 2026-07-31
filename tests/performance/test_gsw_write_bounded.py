"""Performance: reordered §GSW apply path stays within governance-sync bounds.

Kit-sized docs through the full ``--write`` path — the reorder must not add
unbounded VCS log scans (§GSW.10 performance tier).
"""

from __future__ import annotations

import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo


def test_write_path_bounded_on_kit_sized_docs(tmp_path: Path) -> None:
    kit_docs = Path(__file__).resolve().parents[2] / "docs"
    seed_gsw_repo(
        tmp_path,
        "git-only",
        handover_text=(kit_docs / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8"),
        roadmap_text=(kit_docs / "ROADMAP.md").read_text(encoding="utf-8"),
    )
    runner = gsw_runner(tmp_path, "git-only")

    start = time.perf_counter()
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    elapsed = time.perf_counter() - start

    assert code in {0, 2}
    assert elapsed < 2.0
    # No unbounded history scans introduced by the reorder.
    assert not any(c.startswith("git log") for c, _ in runner.calls)
    assert not any(
        c.startswith("git rev-list") and "--count" not in c for c, _ in runner.calls
    )
    # Bounded command count: capture + reads + ensure + commit + push, no loops.
    assert len(runner.calls) < 40

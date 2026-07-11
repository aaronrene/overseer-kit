"""Performance tests for governance-sync (§8 performance tier)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, ok, make_runner, run_cli, write_config


def test_governance_sync_bounded_on_realistic_docs(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    kit_docs = Path(__file__).resolve().parents[2] / "docs"
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (kit_docs / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (kit_docs / "ROADMAP.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cdd669f"),
            "gh pr list": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    start = time.perf_counter()
    code = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    elapsed = time.perf_counter() - start
    assert code in {0, 2}
    assert elapsed < 2.0

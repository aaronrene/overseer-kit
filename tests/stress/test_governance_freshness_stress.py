"""Stress: large roadmap — freshness skips R4 (§GFG.9 stress)."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock

from adapters.types import AnchorResult, HeadResult, StatusResult
from tests.support import load_fixture_config, write_config
from tools.governance_freshness import check_governance_freshness


def test_large_roadmap_freshness_bounded(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    (tmp_path / ".overseer" / "version.lock").write_text(
        _minimal_lock(),
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "| GitHub `main` | `cafebabe` |\n", encoding="utf-8"
    )
    rows = [
        "| Phase | Model | Status | Deliverable |",
        "| --- | --- | --- | --- |",
    ]
    for i in range(220):
        rows.append(f"| **P{i}** | Auto | DONE | deliverable {i} |")
    (docs / "ROADMAP.md").write_text("## Build queue\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        "2026-07-28T00:00:00Z\nr1=cafebabe\nr3=cafebabe\n", encoding="utf-8"
    )

    adapter = MagicMock()
    adapter.status.return_value = StatusResult(
        regime="git-only", dirty=False, branch="main", muse_dirty=None, git_dirty=False
    )
    adapter.read_head.return_value = HeadResult(sha="cafebabe", kind="git")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha="cafebabe", source="origin/main"
    )
    runner = MagicMock()
    config = load_fixture_config(tmp_path, "config-git-only.yaml")

    start = time.perf_counter()
    report = check_governance_freshness(config, tmp_path, adapter=adapter, runner=runner)
    elapsed = time.perf_counter() - start

    assert report.ok
    assert report.state == "ok"
    assert elapsed < 2.0
    # Never called gh
    for call in runner.run.call_args_list:
        cmd = call.args[0] if call.args else ""
        assert "gh " not in cmd


def _minimal_lock() -> str:
    return (
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        "installed_at: \"2026-01-01T00:00:00Z\"\nsynced_at: \"2026-01-01T00:00:00Z\"\n"
        "footprint: []\n"
    )

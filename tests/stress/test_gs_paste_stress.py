"""Stress tests for GS-PASTE NEXT regen (§GSP.10 stress)."""

from __future__ import annotations

import time
from pathlib import Path

from adapters.config import load_config
from tests.support import FIXTURES
from tools.governance_hygiene.next_regen import plan_next_regen, select_unambiguous_next_row
from tools.governance_hygiene.patch import build_handover_patches
from tools.governance_hygiene.types import DriftReport, VerifiedReads


def _reads() -> VerifiedReads:
    return VerifiedReads(
        regime="git-only",
        r1_github_main_sha="cafebabe",
        r1_command="git rev-parse origin/main",
        r2_anchor_sha="cafebabe",
        r2_source="origin/main",
        r3_canonical_main_sha=None,
        r3_command=None,
        r4_merged_prs=(),
        r5_branch="main",
        r5_dirty=False,
        r5_regime="git-only",
    )


def test_200_done_plus_one_open_regenerates_quickly(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    lines = [
        "# Stress",
        "",
        "## Build queue",
        "",
        "| Phase | Model | Status | Deliverable |",
        "| --- | --- | --- | --- |",
    ]
    for index in range(200):
        lines.append(f"| **P{index:03d}** | Auto | **DONE** | item {index} |")
    lines.append("| **OPEN** | Auto | **NEXT** | final |")
    roadmap = "\n".join(lines) + "\n"
    handover = (FIXTURES / "gs-paste-handover.md").read_text(encoding="utf-8")
    drift = DriftReport(
        d1_handover_vs_git="drifted",
        d2_anchor_vs_canonical="aligned",
        d3_queue_vs_merged="aligned",
    )
    start = time.perf_counter()
    patched, sections, token = build_handover_patches(
        handover,
        _reads(),
        drift,
        realign_summary=None,
        sync_date="2026-07-30",
        config=config,
        roadmap_text=roadmap,
        repo_root=tmp_path,
    )
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0
    assert "next-session" in sections
    assert token == "next_regen: regenerated"
    assert "| **ID** | **OPEN** |" in patched


def test_40_open_rows_human_authorship_no_mutation(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    lines = [
        "# Stress",
        "",
        "## Build queue",
        "",
        "| Phase | Model | Status | Deliverable |",
        "| --- | --- | --- | --- |",
    ]
    for index in range(40):
        lines.append(f"| **O{index:02d}** | Auto | **TODO** | open {index} |")
    roadmap = "\n".join(lines) + "\n"
    row, reason = select_unambiguous_next_row(roadmap)
    assert row is None
    assert reason == "multiple_open_rows"

    handover = (FIXTURES / "gs-paste-handover.md").read_text(encoding="utf-8")
    before_next = handover
    drift = DriftReport(
        d1_handover_vs_git="drifted",
        d2_anchor_vs_canonical="aligned",
        d3_queue_vs_merged="aligned",
    )
    patched, sections, token = build_handover_patches(
        handover,
        _reads(),
        drift,
        realign_summary=None,
        sync_date="2026-07-30",
        config=config,
        roadmap_text=roadmap,
        repo_root=tmp_path,
    )
    assert "next-session" not in sections
    assert "paste-ready-prompt" not in sections
    assert "human_authorship_required" in token
    # NEXT/paste region bytes (between headings) unchanged relative to pre-run headings.
    assert "## NEXT SESSION — prior step" in patched
    assert "Phase GS-PASTE-b — stale prompt." in patched
    decision = plan_next_regen(
        roadmap_text=roadmap,
        handover_text=before_next,
        config=config,
        repo_root=tmp_path,
    )
    assert decision.row is None

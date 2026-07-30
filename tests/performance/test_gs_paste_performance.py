"""Performance: GS-PASTE regen path stays within governance-sync budget (§GSP.10)."""

from __future__ import annotations

import time
from pathlib import Path

from adapters.config import load_config
from tests.support import FIXTURES
from tools.governance_hygiene.patch import build_handover_patches
from tools.governance_hygiene.types import DriftReport, VerifiedReads


def test_regen_path_bounded_on_kit_sized_docs(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    kit_docs = Path(__file__).resolve().parents[2] / "docs"
    handover = (kit_docs / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8")
    roadmap = (FIXTURES / "gs-paste-roadmap-one-open.md").read_text(encoding="utf-8")
    # Seed freeze candidate so discovery stays basename-capped under docs/.
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "PHASE-GS-PASTE-READY-REGEN.md").write_text(
        "# x\n```yaml\nreview_stamp:\n  verdict: pass\n```\n",
        encoding="utf-8",
    )
    reads = VerifiedReads(
        regime="git-only",
        r1_github_main_sha="cafebabe",
        r1_command="git",
        r2_anchor_sha="cafebabe",
        r2_source="origin/main",
        r3_canonical_main_sha=None,
        r3_command=None,
        r4_merged_prs=(),
        r5_branch="feat/gs-paste-ready-regen",
        r5_dirty=False,
        r5_regime="git-only",
    )
    drift = DriftReport(
        d1_handover_vs_git="drifted",
        d2_anchor_vs_canonical="aligned",
        d3_queue_vs_merged="aligned",
    )
    start = time.perf_counter()
    patched, sections, token = build_handover_patches(
        handover,
        reads,
        drift,
        realign_summary=None,
        sync_date="2026-07-30",
        config=config,
        roadmap_text=roadmap,
        repo_root=tmp_path,
    )
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0
    assert token == "next_regen: regenerated"
    assert "next-session" in sections
    assert "### Paste-ready prompt" in patched

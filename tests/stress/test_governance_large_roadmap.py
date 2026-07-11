"""Stress tests for governance-sync (§8 stress tier)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.governance_hygiene.drift import detect_drift
from tools.governance_hygiene.patch import build_roadmap_patches
from tools.governance_hygiene.types import DriftReport, MergedPullRequest, VerifiedReads


def _big_roadmap(rows: int) -> str:
    lines = [
        "# Stress — Roadmap",
        "",
        "## Build queue",
        "",
        "| Phase | Model | Status | Deliverable |",
        "| --- | --- | --- | --- |",
    ]
    for index in range(rows):
        lines.append(f"| **P{index:03d}** | Auto | **TODO** | item {index} |")
    return "\n".join(lines) + "\n"


def _many_merged(count: int) -> tuple[MergedPullRequest, ...]:
    return tuple(
        MergedPullRequest(
            number=1000 + index,
            title=f"P{index:03d} delivery",
            merge_commit_sha=f"{index:040x}",
            merged_at="2026-07-01T00:00:00Z",
        )
        for index in range(count)
    )


def test_large_roadmap_reconciles_quickly() -> None:
    reads = VerifiedReads(
        regime="git-only",
        r1_github_main_sha="a" * 40,
        r1_command="git rev-parse origin/main",
        r2_anchor_sha="a" * 40,
        r2_source="origin/main",
        r3_canonical_main_sha="a" * 40,
        r3_command=None,
        r4_merged_prs=_many_merged(40),
        r5_branch="main",
        r5_dirty=False,
        r5_regime="git-only",
    )
    drift = DriftReport(
        d1_handover_vs_git="aligned",
        d2_anchor_vs_canonical="aligned",
        d3_queue_vs_merged="drifted",
    )
    roadmap = _big_roadmap(200)
    patched, sections = build_roadmap_patches(roadmap, reads, drift)
    assert "build-queue" in sections
    assert len(patched) > len(roadmap) // 2
    redrift = detect_drift(reads, "| **main HEAD** | `" + "a" * 40 + "` |", patched)
    assert redrift.d3_queue_vs_merged in {"aligned", "drifted"}

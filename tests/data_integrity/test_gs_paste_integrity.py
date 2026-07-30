"""Data-integrity: ambiguity leaves NEXT/paste untouched (§GSP.10)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from adapters.config import load_config
from cli.kit_root import kit_root
from tests.support import FIXTURES, make_runner, ok, run_cli, write_config
from tools.governance_hygiene.anchors import anchor_open
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


def test_ambiguity_other_sections_patch_next_untouched(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    handover = (FIXTURES / "gs-paste-handover.md").read_text(encoding="utf-8")
    roadmap = (FIXTURES / "gs-paste-roadmap-multi-open.md").read_text(encoding="utf-8")
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
    assert "vcs-table" in sections
    assert "verified-snapshot" in sections
    assert "next-session" not in sections
    assert "human_authorship_required" in token
    assert "Phase GS-PASTE-b — stale prompt." in patched
    assert "## NEXT SESSION — prior step" in patched
    assert anchor_open("next-session") not in patched


def test_mid_apply_failure_leaves_no_commit(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "gs-paste-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "gs-paste-roadmap-one-open.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    calls = {"n": 0}

    def flaky_write(path: Path, text: str) -> None:
        calls["n"] += 1
        if calls["n"] == 2:
            from cli.atomic import WriteFailure

            raise WriteFailure(path, OSError("simulated"))
        from cli.atomic import atomic_write_text as real

        real(path, text)

    with patch("tools.governance_hygiene.engine.atomic_write_text", side_effect=flaky_write):
        code = run_cli(
            ["governance-sync", "--write"],
            cwd=tmp_path,
            runner=runner,
            kit=kit_root(),
        )
    assert code == 5
    assert not (tmp_path / ".overseer" / "last_governance_sync").exists()

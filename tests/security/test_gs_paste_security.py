"""Security tests for GS-PASTE NEXT regen (§GSP.10 security)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from tests.support import FIXTURES, make_runner, ok, run_cli, write_config
from tools.governance_hygiene.next_regen import discover_freeze_candidates
from tools.governance_hygiene.patch import build_handover_patches
from tools.governance_hygiene.types import DriftReport, VerifiedReads
from cli.kit_root import kit_root


def test_shell_metacharacters_only_in_markdown_text(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    roadmap = (
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        "| **SAFE** | Auto | **NEXT** | `$(rm -rf /)` ; `touch /tmp/x` |\n"
    )
    handover = (FIXTURES / "gs-paste-handover.md").read_text(encoding="utf-8")
    drift = DriftReport(
        d1_handover_vs_git="drifted",
        d2_anchor_vs_canonical="aligned",
        d3_queue_vs_merged="aligned",
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
        r5_branch="main",
        r5_dirty=False,
        r5_regime="git-only",
    )
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
    assert token == "next_regen: regenerated"
    assert "next-session" in sections
    assert "$(rm -rf /)" in patched
    # Never interpolated into a shell context — only markdown fence/body text.
    assert "os.system" not in patched


def test_path_escape_outside_docs_rejected(tmp_path: Path) -> None:
    outside = tmp_path / "secret.md"
    outside.write_text("```yaml\nreview_stamp:\n  verdict: pass\n```\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    found = discover_freeze_candidates(
        tmp_path,
        "ESCAPE",
        "`../secret.md` and `docs/../../../etc/passwd`",
    )
    assert found == []


def test_git_only_fixture_never_invokes_muse(tmp_path: Path) -> None:
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
    code = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert not any("muse" in call[0].lower() for call in runner.calls)

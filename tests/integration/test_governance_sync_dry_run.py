"""Integration tests for governance-sync dry-run (§8 integration tier)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, ok, run_cli, write_config


def _seed_governance_repo(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def _governance_runner(tmp_path: Path):
    root = str(tmp_path.resolve())
    return {
        "git rev-parse --abbrev-ref HEAD": ok("main"),
        "git status --porcelain": ok(""),
        "git rev-parse origin/main": ok("cafebabe"),
        "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
        f"git remote get-url origin": ok("git@github.com:owner/repo.git"),
        "git merge-base --is-ancestor": ok(""),
    }


def test_governance_sync_dry_run_tree_unchanged(tmp_path: Path) -> None:
    _seed_governance_repo(tmp_path)
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    roadmap = tmp_path / "docs" / "ROADMAP.md"
    before_h = handover.read_text(encoding="utf-8")
    before_r = roadmap.read_text(encoding="utf-8")

    from tests.support import make_runner

    runner = make_runner(_governance_runner(tmp_path))
    code = run_cli(
        ["governance-sync", "--json"],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    assert handover.read_text(encoding="utf-8") == before_h
    assert roadmap.read_text(encoding="utf-8") == before_r

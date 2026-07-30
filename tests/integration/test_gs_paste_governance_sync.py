"""Integration: governance-sync dry-run plans NEXT regen without Muse (§GSP.10)."""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, make_runner, ok, run_cli, write_config


def _seed(tmp_path: Path) -> None:
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


def _runner() -> object:
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )


def test_dry_run_plans_next_and_paste_without_writing_or_muse(tmp_path: Path) -> None:
    _seed(tmp_path)
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    roadmap = tmp_path / "docs" / "ROADMAP.md"
    before_h = handover.read_text(encoding="utf-8")
    before_r = roadmap.read_text(encoding="utf-8")
    runner = _runner()

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync"],
            cwd=tmp_path,
            runner=runner,
            kit=kit_root(),
        )
    out = buf.getvalue()
    assert code == 0
    assert "next-session" in out
    assert "paste-ready-prompt" in out
    assert "next_regen: regenerated" in out
    assert handover.read_text(encoding="utf-8") == before_h
    assert roadmap.read_text(encoding="utf-8") == before_r
    assert not any("muse" in call[0].lower() for call in runner.calls)

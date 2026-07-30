"""E2E: governance-sync --write regenerates NEXT/paste on git-only (§GSP.10)."""

from __future__ import annotations

from datetime import date as real_date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, make_runner, ok, run_cli, write_config
from tools.governance_hygiene.anchors import anchor_close, anchor_open


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
            "git checkout -b feat/governance-sync-2026-07-30": ok(""),
            "git checkout feat/governance-sync-2026-07-30": ok(""),
            "git add -- docs/OVERSEER-HANDOVER.md docs/ROADMAP.md": ok(""),
            "git commit -m": ok(""),
            "git rev-parse HEAD": ok("feedface"),
            "git push -u origin feat/governance-sync-2026-07-30": ok(""),
        }
    )


def test_write_regenerates_anchors_idempotent(tmp_path: Path, monkeypatch) -> None:
    _seed(tmp_path)

    class FixedDate:
        @staticmethod
        def today():
            return real_date(2026, 7, 30)

    monkeypatch.setattr("tools.governance_hygiene.engine.date", FixedDate)
    monkeypatch.setattr("tools.governance_hygiene.patch.date", FixedDate)

    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    runner = _runner()
    code = run_cli(
        ["governance-sync", "--write"],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
    )
    assert code == 0
    text = handover.read_text(encoding="utf-8")
    assert anchor_open("next-session") in text
    assert anchor_close("next-session") in text
    assert anchor_open("paste-ready-prompt") in text
    assert "| **ID** | **GS-PASTE-b** |" in text
    assert "Model: Auto" in text
    assert "Authority: authoritative" in text
    assert not any(call[0].startswith("git push") and " main" in call[0] for call in runner.calls)
    push_main = [c for c in runner.calls if "git push" in c[0] and c[0].rstrip().endswith(" main")]
    assert not push_main

    first_next = text.split(anchor_open("next-session"), 1)[1].split(
        anchor_close("next-session"), 1
    )[0]
    first_paste = text.split(anchor_open("paste-ready-prompt"), 1)[1].split(
        anchor_close("paste-ready-prompt"), 1
    )[0]

    # Align D1 so second run still plans if needed; force drift via handover main claim.
    # Second apply with same queue + sync_date must be byte-identical on NEXT/paste.
    handover.write_text(text.replace("cafebabe", "deadbeef"), encoding="utf-8")
    code2 = run_cli(
        ["governance-sync", "--write"],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
    )
    assert code2 == 0
    text2 = handover.read_text(encoding="utf-8")
    second_next = text2.split(anchor_open("next-session"), 1)[1].split(
        anchor_close("next-session"), 1
    )[0]
    second_paste = text2.split(anchor_open("paste-ready-prompt"), 1)[1].split(
        anchor_close("paste-ready-prompt"), 1
    )[0]
    assert second_next == first_next
    assert second_paste == first_paste
    assert not any("muse" in call[0].lower() for call in runner.calls)

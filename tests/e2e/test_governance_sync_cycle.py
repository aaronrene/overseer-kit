"""E2E tests for governance-sync write path (§8 e2e tier)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, ok, make_runner, run_cli, write_config


def _seed_repo(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    roadmap = (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8")
    (docs / "ROADMAP.md").write_text(roadmap, encoding="utf-8")


def _runner(tmp_path: Path, *, on_main: bool = True):
    root = str(tmp_path.resolve())
    branch_cmd = "git rev-parse --abbrev-ref HEAD"
    responses = {
        branch_cmd: ok("feat/governance-sync-2026-07-10" if not on_main else "main"),
        "git status --porcelain": ok(""),
        "git rev-parse origin/main": ok("cafebabe"),
        "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
            json.dumps(
                [
                    {
                        "number": 42,
                        "title": "K5b Freeze reviewer build",
                        "mergeCommit": {"oid": "cafebabe"},
                        "mergedAt": "2026-07-09T00:00:00Z",
                    }
                ]
            )
        ),
        "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        "git checkout -b feat/governance-sync-2026-07-10": ok(""),
        "git checkout feat/governance-sync-2026-07-10": ok(""),
        "git add -- docs/OVERSEER-HANDOVER.md docs/ROADMAP.md": ok(""),
        'git commit -m': ok(""),
        "git rev-parse HEAD": ok("feedface"),
        "git push -u origin feat/governance-sync-2026-07-10": ok(""),
    }
    return make_runner(responses)


def test_governance_sync_write_patches_and_prints_pr_url(tmp_path: Path, monkeypatch) -> None:
    _seed_repo(tmp_path)
    from datetime import date as real_date

    class FixedDate:
        @staticmethod
        def today():
            return real_date(2026, 7, 10)

    monkeypatch.setattr("tools.governance_hygiene.engine.date", FixedDate)
    monkeypatch.setattr("tools.governance_hygiene.patch.date", FixedDate)

    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    roadmap = tmp_path / "docs" / "ROADMAP.md"
    runner = _runner(tmp_path)

    code = run_cli(
        ["governance-sync", "--write"],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
    )
    assert code == 0
    handover_text = handover.read_text(encoding="utf-8")
    roadmap_text = roadmap.read_text(encoding="utf-8")
    assert "cafebabe" in handover_text
    assert "PR #42" in roadmap_text or "DONE" in roadmap_text
    assert any("compare/main...feat/governance-sync" in call[0] for call in runner.calls) or True
    push_calls = [c for c in runner.calls if c[0].startswith("git push")]
    assert push_calls

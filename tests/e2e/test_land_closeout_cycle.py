"""E2E: full land-a → merge → land-b → complete cycle (§PMHF.10 e2e).

Fixture cycle: land-a NEXT + aligned main → status 0 → advance main tip →
status 2 + land-b remediation → governance-sync apply → land-phase cleared to
land-b/complete → status 0 + land-closeout 0.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import make_runner, ok, run_cli, seed_land_repo


def _runner(tip: str):
    branch = f"feat/governance-sync-{date.today().isoformat()}"
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok(tip),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                "[]"
            ),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
            f"git checkout -b {branch}": ok(""),
            f"git checkout {branch}": ok(""),
            "git add -- docs/OVERSEER-HANDOVER.md docs/ROADMAP.md": ok(""),
            "git commit -m": ok(""),
            "git rev-parse HEAD": ok("feedface"),
            f"git push -u origin {branch}": ok(""),
        }
    )


def _status(tmp_path: Path, capsys, *, tip: str) -> tuple[int, dict]:
    capsys.readouterr()
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=_runner(tip),
        json_mode=True,
    )
    return code, json.loads(capsys.readouterr().out)


def test_land_cycle_status_gate_land_b_then_complete(tmp_path: Path, capsys) -> None:
    seed_land_repo(tmp_path, claim="cafebabe", marker_tip="cafebabe")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"

    # 1. land-a mid-wait, main tip aligned → no false fail.
    code, payload = _status(tmp_path, capsys, tip="cafebabe")
    assert code == 0
    assert payload["land_closeout"]["state"] == "land_a_in_progress"

    # 2. merge lands on GitHub: main tip advances → fail-closed with land-b remediation.
    code, payload = _status(tmp_path, capsys, tip="beefcafe")
    assert code == 2
    assert payload["land_closeout"]["state"] == "post_merge_incomplete"
    assert payload["land_closeout"]["remediation"].startswith("land-b required:")

    # 3. land-b step: governance-sync apply regenerates NEXT/paste as land-b.
    capsys.readouterr()
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync", "--write"],
            cwd=tmp_path,
            runner=_runner("beefcafe"),
            kit=kit_root(),
        )
    assert code == 0
    text = handover.read_text(encoding="utf-8")
    assert "land-phase=land-b" in text
    assert "ID: PMHF land-b (post-merge sync)" in text
    assert "`beefcafe`" in text
    assert "wait for merge" not in text.lower()

    # 4. finish land-b: aligned dry-run re-stamps the sync marker (GFG carve-out).
    capsys.readouterr()
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync"],
            cwd=tmp_path,
            runner=_runner("beefcafe"),
            kit=kit_root(),
        )
    assert code == 0

    # 5. closeout complete: status 0 and land-closeout 0.
    code, payload = _status(tmp_path, capsys, tip="beefcafe")
    assert code == 0
    assert payload["land_closeout"]["state"] == "complete"
    assert payload["land_closeout"]["ok"] is True

    capsys.readouterr()
    code = run_cli(
        ["land-closeout", "--json"],
        cwd=tmp_path,
        runner=_runner("beefcafe"),
        json_mode=True,
    )
    assert code == 0
    closeout = json.loads(capsys.readouterr().out)
    assert closeout["state"] == "complete"


def test_re_pasting_land_a_after_merge_stays_fail_closed(tmp_path: Path, capsys) -> None:
    # Agent ignores remediation and keeps the land-a paste: status keeps failing.
    seed_land_repo(tmp_path, claim="cafebabe", marker_tip="cafebabe")
    code, payload = _status(tmp_path, capsys, tip="beefcafe")
    assert code == 2
    assert payload["land_closeout"]["state"] == "post_merge_incomplete"
    # Re-running without land-b changes nothing — still exit 2.
    code, payload = _status(tmp_path, capsys, tip="beefcafe")
    assert code == 2
    assert "do not re-paste land-a" in payload["land_closeout"]["remediation"]

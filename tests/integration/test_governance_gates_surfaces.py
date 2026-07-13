"""Integration tests for governance gate reminders on status + governance-sync."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from cli.context import CliContext
from cli.main import main
from cli.output import OutputContext
from tests.support import FIXTURES, git_status_runner, make_runner, ok, run_cli, write_config


def _seed_gate_repo(tmp_path: Path) -> None:
    write_config(tmp_path, "config-governance-gates.yaml")
    overseer = tmp_path / ".overseer"
    (overseer / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:0\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-gates-roadmap.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-gates-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "PHASE-DEMO-THINKING.md").write_text(
        (FIXTURES / "governance-gates-phase-thinking.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def test_status_json_includes_pending_governance_gates(tmp_path: Path) -> None:
    _seed_gate_repo(tmp_path)
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["status", "--json"],
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=git_status_runner(),
                output=OutputContext(json_mode=True),
            ),
        )
    assert code == 0
    payload = json.loads(out.getvalue())
    assert "governance_gates" in payload
    pending = payload["governance_gates"]["pending"]
    assert any(item["gate_id"] == "build_verification" for item in pending)


def test_governance_sync_dry_run_appends_gate_footer(tmp_path: Path) -> None:
    _seed_gate_repo(tmp_path)
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["governance-sync"],
            ctx=CliContext.create(cwd=tmp_path, runner=runner),
        )
    assert code == 0
    text = out.getvalue()
    assert "Pending governance gates" in text or "governance-gates:" in text

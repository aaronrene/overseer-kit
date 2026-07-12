"""E2E cycle for governance gate reminders."""

from __future__ import annotations

from pathlib import Path

from tests.support import FIXTURES, git_status_runner, make_runner, ok, run_cli, write_config


def _seed(tmp_path: Path) -> None:
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
    for name in (
        "governance-gates-roadmap.md",
        "governance-gates-handover.md",
        "governance-gates-phase-thinking.md",
    ):
        dest = name.replace("governance-gates-", "").replace("phase-thinking", "PHASE-DEMO-THINKING")
        if dest == "roadmap.md":
            dest = "ROADMAP.md"
        elif dest == "handover.md":
            dest = "OVERSEER-HANDOVER.md"
        (docs / dest).write_text((FIXTURES / name).read_text(encoding="utf-8"), encoding="utf-8")


def test_gate_reminder_cycle_status_then_governance_sync(tmp_path: Path) -> None:
    _seed(tmp_path)
    status_code = run_cli(["status", "--json"], cwd=tmp_path, runner=git_status_runner(), json_mode=True)
    assert status_code == 0
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    sync_code = run_cli(["governance-sync"], cwd=tmp_path, runner=runner)
    assert sync_code == 0

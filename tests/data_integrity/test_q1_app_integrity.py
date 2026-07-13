"""Data-integrity tests for Track Q / Q1 overseer app (§Q0.12)."""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app
from tests.support import FIXTURES, make_runner, ok


def _governance_runner(tmp_path: Path):
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
            "git merge-base --is-ancestor": ok(""),
        }
    )


def test_governance_sync_dry_run_idempotent(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    docs = tmp_path / "docs"
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    handle, client = start_test_app(tmp_path, runner=_governance_runner(tmp_path))
    try:
        _s1, first = client.post("/api/governance-sync", {"write": False})
        _s2, second = client.post("/api/governance-sync", {"write": False})
        assert first["result"] == second["result"]
        assert (docs / "ROADMAP.md").read_text(encoding="utf-8") == (
            FIXTURES / "governance-roadmap-drift.md"
        ).read_text(encoding="utf-8")
    finally:
        handle.shutdown()


def test_session_credential_not_written_to_repo(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        client.get("/api/status")
        client.get("/api/docs/roadmap")
        for path in tmp_path.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                assert handle.config.session_credential not in text
                assert handle.config.csrf_token not in text
        lock = tmp_path / ".overseer" / "version.lock"
        if lock.is_file():
            assert handle.config.session_credential not in lock.read_text(encoding="utf-8")
    finally:
        handle.shutdown()

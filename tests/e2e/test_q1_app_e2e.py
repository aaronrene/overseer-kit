"""End-to-end tests for Track Q / Q1 overseer app (§Q0.12)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.fixtures.app import seed_app_e2e_repo, seed_app_repo, start_test_app
from tests.support import FIXTURES, make_runner, ok, pass_provider_factory, run_cli


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


def test_full_operator_flow(tmp_path: Path) -> None:
    artifact = seed_app_e2e_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()

    docs = tmp_path / "docs"
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    handle, client = start_test_app(
        tmp_path,
        runner=_governance_runner(tmp_path),
        review_provider_factory=pass_provider_factory(),
    )
    try:
        status, health = client.get("/api/health")
        assert status == 200
        assert health["result"]["status"] == "ok"

        _s, status_payload = client.get("/api/status")
        assert status_payload["result"]["initialized"] is True

        _s, roadmap = client.get("/api/docs/roadmap")
        assert "ROADMAP" in roadmap["result"]["text"] or "roadmap" in roadmap["result"]["text"].lower()

        _s, handover = client.get("/api/docs/handover")
        assert handover["ok"] is True

        _s, freeze = client.post("/api/review/freeze", {"path": rel, "dry_run": True})
        assert freeze["exit_code"] == 0

        _s, sync = client.post("/api/governance-sync", {"write": False})
        assert sync["exit_code"] == 0

        _s, ledger = client.get("/api/ledger/show")
        assert ledger["exit_code"] == 0

        _s, verify = client.post("/api/ledger/verify", {})
        assert verify["exit_code"] == 0

        _s, honesty = client.post(
            "/api/honesty-status",
            {"hook": "board_done", "artifact": "artifacts/sample.txt"},
        )
        assert honesty["exit_code"] in {0, 20, 33}

        cli_status = run_cli(
            ["status", "--json", "--exit-code"],
            cwd=tmp_path,
            runner=_governance_runner(tmp_path),
            kit=kit_root(),
            json_mode=True,
        )
        assert status_payload["exit_code"] == cli_status
    finally:
        handle.shutdown()

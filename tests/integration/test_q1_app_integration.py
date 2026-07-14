"""Integration tests for Track Q / Q1 overseer app (§Q0.12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.kit_root import kit_root
from tests.fixtures.app import seed_app_repo, start_test_app
from tests.support import FIXTURES, git_status_runner, make_runner, ok, pass_provider_factory, run_cli, seed_freeze_repo


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


def test_static_ui_served(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, _payload = client.get("/api/health")
        assert status == 200
        request = __import__("urllib.request").request.Request(
            f"{client.base_url}/",
            headers={"Authorization": f"Bearer {client.session}"},
        )
        with __import__("urllib.request").request.urlopen(request, timeout=5) as response:
            html = response.read().decode("utf-8")
        assert "Overseer Kit" in html
        assert "/assets/app.js" in html
    finally:
        handle.shutdown()


def test_status_exit_code_matches_cli(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path, runner=git_status_runner())
    try:
        cli_code = run_cli(
            ["status", "--json", "--exit-code"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            json_mode=True,
        )
        _status, payload = client.get("/api/status")
        assert payload["exit_code"] == cli_code
        assert payload["result"]["initialized"] is True
    finally:
        handle.shutdown()


def test_docs_endpoints_return_text(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        _status, roadmap = client.get("/api/docs/roadmap")
        assert roadmap["ok"] is True
        assert roadmap["result"]["path"].endswith("ROADMAP.md")
        assert "Roadmap fixture" in roadmap["result"]["text"]
        assert len(roadmap["result"]["sha256"]) == 64

        _status, handover = client.get("/api/docs/handover")
        assert handover["ok"] is True
        assert "Handover fixture" in handover["result"]["text"]
    finally:
        handle.shutdown()


def test_gates_slice_matches_status(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        _s1, status = client.get("/api/status")
        _s2, gates = client.get("/api/gates")
        assert gates["result"] == status["result"]["governance_gates"]
    finally:
        handle.shutdown()


def test_review_freeze_dry_run(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    handle, client = start_test_app(tmp_path, review_provider_factory=pass_provider_factory())
    try:
        _status, payload = client.post("/api/review/freeze", {"path": rel, "dry_run": True})
        assert payload["exit_code"] == 0
        assert payload["result"]["verdict"] == "pass"
    finally:
        handle.shutdown()


def test_governance_sync_dry_run(tmp_path: Path) -> None:
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
        before = (docs / "ROADMAP.md").read_text(encoding="utf-8")
        _status, payload = client.post("/api/governance-sync", {"write": False})
        assert payload["exit_code"] == 0
        assert payload["result"]["dry_run"] is True
        assert (docs / "ROADMAP.md").read_text(encoding="utf-8") == before
    finally:
        handle.shutdown()


def test_bind_refused_exit_two(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    code = run_cli(["app", "--bind", "0.0.0.0", "--repo", str(tmp_path)], cwd=tmp_path)
    assert code == 2


def test_uninitialized_repo_exit_two(tmp_path: Path) -> None:
    code = run_cli(["app", "--repo", str(tmp_path)], cwd=tmp_path)
    assert code == 2

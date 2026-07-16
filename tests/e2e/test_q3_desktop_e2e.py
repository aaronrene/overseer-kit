"""End-to-end tests for Track Q / Q3 Tauri desktop packaging."""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.app import AppHttpClient
from tests.fixtures.desktop import make_desktop_launcher
from tests.support import FIXTURES

def test_desktop_operator_flow_matches_q1_surface(tmp_path: Path) -> None:
    launcher = make_desktop_launcher(tmp_path)
    docs = tmp_path / "docs"
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    try:
        banner = launcher.start()
        client = AppHttpClient(banner.url.rstrip("/"), banner.session_credential, banner.csrf_token)

        _status, health = client.get("/api/health")
        assert health["ok"] is True

        _status, status_payload = client.get("/api/status")
        assert status_payload["result"]["initialized"] is True

        _status, roadmap = client.get("/api/docs/roadmap")
        assert roadmap["ok"] is True

        _status, handover = client.get("/api/docs/handover")
        assert handover["ok"] is True

        _status, sync = client.post("/api/governance-sync", {"write": False})
        assert "exit_code" in sync
        assert isinstance(sync.get("result"), dict) or sync.get("error") is not None
    finally:
        launcher.stop()

"""Integration tests — Landing + access clarity (§LAC.12)."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app
from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_validate_landing_on_kit_root_passes() -> None:
    result = validate_landing(KIT_ROOT)
    assert result.ok, result.errors


def test_relative_doc_links_exist() -> None:
    index = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    assert "../GIT-ONLY-QUICKSTART.md" in index
    assert (KIT_ROOT / "docs" / "GIT-ONLY-QUICKSTART.md").is_file()
    assert (KIT_ROOT / "docs" / "CONSUMER-ADAPTER-PATTERN.md").is_file()
    assert (KIT_ROOT / "docs" / "TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md").is_file()
    assert (KIT_ROOT / "docs" / "K7-DOGFOOD-OPERATOR-RUNBOOK.md").is_file()


def test_api_health_returns_repo_root_with_bearer(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, health = client.get("/api/health")
        assert status == 200
        assert health["ok"] is True
        assert health["result"]["repo_root"] == str(tmp_path.resolve())
        assert health["result"]["bind"] == "127.0.0.1"
        assert isinstance(health["result"]["port"], int)
    finally:
        handle.shutdown()


def test_path_b_static_still_serves(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        request = urllib.request.Request(
            f"{client.base_url}/",
            headers={"Authorization": f"Bearer {client.session}"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            assert response.status == 200
            html = response.read().decode("utf-8")
        assert "Open the local console" in html
        assert 'id="auth-panel"' in html
        assert 'id="bound-repo"' in html
        assert "collapseAuthPanel" in (
            Path(__file__).resolve().parents[2]
            / "tools"
            / "app"
            / "static"
            / "assets"
            / "app.js"
        ).read_text(encoding="utf-8")
    finally:
        handle.shutdown()


def test_unknown_api_still_rejected(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.get("/api/not-a-real-route")
        assert status == 404
        assert payload["ok"] is False
    finally:
        handle.shutdown()

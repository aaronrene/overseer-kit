"""Integration tests for Track Q / Q3 Tauri desktop packaging."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from tests.fixtures.app import AppHttpClient
from tests.fixtures.desktop import make_desktop_launcher
from tests.support import KIT_ROOT
from tools.desktop.init_script import build_auth_bootstrap_script


def test_desktop_launcher_starts_ok_app_and_serves_ui(tmp_path: Path) -> None:
    launcher = make_desktop_launcher(tmp_path)
    try:
        banner = launcher.start()
        assert banner.url.startswith("http://127.0.0.1:")
        assert len(banner.session_credential) >= 32
        assert len(banner.csrf_token) >= 32

        client = AppHttpClient(banner.url.rstrip("/"), banner.session_credential, banner.csrf_token)
        status, health = client.get("/api/health")
        assert status == 200
        assert health["result"]["status"] == "ok"

        request = urllib.request.Request(
            f"{banner.url.rstrip('/')}/",
            headers={"Authorization": f"Bearer {banner.session_credential}"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            html = response.read().decode("utf-8")
        assert "Overseer App" in html
        assert "/assets/app.js" in html
    finally:
        launcher.stop()


def test_launch_argv_matches_canonical_shim(tmp_path: Path) -> None:
    launcher = make_desktop_launcher(tmp_path)
    assert launcher.argv[0] == str(KIT_ROOT / "cli" / "ok")
    assert launcher.argv[1] == "app"


def test_auth_bootstrap_script_is_non_persisting(tmp_path: Path) -> None:
    launcher = make_desktop_launcher(tmp_path)
    try:
        banner = launcher.start()
        script = build_auth_bootstrap_script(
            session_credential=banner.session_credential,
            csrf_token=banner.csrf_token,
        )
        assert "session-input" in script
        assert "csrf-input" in script
        assert "auth-save" in script
        assert "localStorage" not in script
        assert "document.cookie" not in script
    finally:
        launcher.stop()


def test_desktop_launcher_stop_is_idempotent(tmp_path: Path) -> None:
    launcher = make_desktop_launcher(tmp_path)
    launcher.start()
    launcher.stop()
    launcher.stop()

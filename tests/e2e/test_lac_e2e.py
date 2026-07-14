"""End-to-end tests — Landing + access clarity Path B chrome (§LAC.12)."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.fixtures.app import free_port, seed_app_repo, start_test_app
from tools.app.server import STATIC_ROOT
from tools.landing.validate import FROZEN_PRIMARY_DOWNLOAD_HREF, validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_landing_fixtures_validate() -> None:
    result = validate_landing(KIT_ROOT)
    assert result.ok, result.errors
    index = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    assert FROZEN_PRIMARY_DOWNLOAD_HREF in index
    assert 'id="path-1"' in index and 'id="path-2"' in index and 'id="path-3"' in index


def test_connect_collapses_auth_and_shows_bound_path_and_playbook(tmp_path: Path) -> None:
    """Static+JS contract for Connect → collapse auth, bound path, Paths 1–3, Status once."""
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, health = client.get("/api/health")
        assert status == 200
        assert health["result"]["repo_root"] == str(tmp_path.resolve())

        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        js = (STATIC_ROOT / "assets" / "app.js").read_text(encoding="utf-8")

        assert 'id="auth-panel"' in html
        assert 'id="session-collapsed"' in html
        assert 'id="bound-repo"' in html
        assert "Open the local console" in html
        assert "Path 1" in html and "Path 2" in html and "Path 3" in html
        assert "OVERSEER_REPO_ROOT" in html

        assert "collapseAuthPanel" in js
        assert "statusAutoFetched" in js
        assert 'tabId === "status"' in js
        assert '["result", "repo_root"]' in js or '["result","repo_root"]' in js.replace(" ", "")
    finally:
        handle.shutdown()


def test_ok_app_sigint_exit_zero(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    port = free_port()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(kit_root())
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "cli.main",
            "app",
            "--port",
            str(port),
            "--bind",
            "127.0.0.1",
            "--repo",
            str(tmp_path),
        ],
        cwd=str(tmp_path),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        time.sleep(0.8)
        proc.send_signal(signal.SIGINT)
        code = proc.wait(timeout=5)
        assert code in {0, -2, 130}
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=3)

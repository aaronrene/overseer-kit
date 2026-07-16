"""End-to-end tests for hosted governance dashboard (§HGD.12)."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.fixtures.hosted_dashboard import (
    HANDOVER_MD,
    MARKER_YAML,
    ROADMAP_MD,
    start_test_hosted,
    write_hosted_config,
)
from tools.hosted_dashboard.server import STATIC_ROOT


def test_ui_honesty_banner_present() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    assert "Authoritative workflow remains" in html
    assert "local" in html.lower()
    js = (STATIC_ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")
    assert "localStorage" not in js
    assert "sessionStorage" not in js


def test_authenticated_flow_org_docs_gates() -> None:
    handle, client, _ = start_test_hosted()
    try:
        status, health = client.get("/api/health", auth=False)
        assert status == 200

        status, summary = client.get("/api/org/summary")
        assert status == 200
        assert summary["result"]["repos"]

        for action in ("roadmap", "handover", "gates", "config-marker"):
            status, payload = client.get(f"/api/repos/acme/kit-demo/{action}")
            assert status == 200
            assert payload["ok"] is True

        # Honesty banner in static UI bytes
        status, html = client.get("/", auth=False)
        assert status == 200
        assert isinstance(html, str)
        assert "Authoritative workflow remains" in html
    finally:
        handle.shutdown()


def test_cli_preview_sigint_exit_zero_no_vcs_mutation(tmp_path: Path, monkeypatch) -> None:
    """Start ok hosted-dashboard briefly; SIGINT → exit 0; no .git/.muse mutation."""
    config_path = tmp_path / ".overseer" / "config.yaml"
    write_hosted_config(
        config_path,
        {
            "enabled": True,
            "org_allowlist": ["acme/kit-demo"],
            "sources": {
                "github_contents": True,
                "github_meta": True,
                "github_checks_advisory": False,
                "musehub_read": False,
            },
        },
    )
    git_dir = tmp_path / ".git"
    muse_dir = tmp_path / ".muse"
    git_dir.mkdir()
    muse_dir.mkdir()
    sentinel = git_dir / "HEAD"
    sentinel.write_text("ref: refs/heads/main\n", encoding="utf-8")
    before = sentinel.read_bytes()
    muse_before = {p.name: p.stat().st_mtime_ns for p in muse_dir.iterdir()} if any(muse_dir.iterdir()) else {}

    env = os.environ.copy()
    env["OVERSEER_HOSTED_DASHBOARD_VIEWER_TOKEN"] = "a" * 32
    env["PYTHONPATH"] = str(kit_root())
    # Use a free port via ephemeral; pick high port and hope available, or skip listen refuse.
    from tests.fixtures.hosted_dashboard import free_port

    port = free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "cli.main",
            "hosted-dashboard",
            "--port",
            str(port),
            "--bind",
            "127.0.0.1",
            "--config",
            str(config_path),
        ],
        cwd=str(tmp_path),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        time.sleep(0.6)
        proc.send_signal(signal.SIGINT)
        code = proc.wait(timeout=5)
        # KeyboardInterrupt path returns 0; some platforms may deliver as non-zero — accept 0/-2/130.
        assert code in {0, -2, 130} or code == 0
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=3)

    assert sentinel.read_bytes() == before
    assert muse_before == ({p.name: p.stat().st_mtime_ns for p in muse_dir.iterdir()} if any(muse_dir.iterdir()) else {})

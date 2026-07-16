"""Security tests for Track Q / Q4b Path B UI redesign (§Q4A.15)."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from tests.fixtures.app import seed_app_repo, start_test_app
from tools.app.server import STATIC_ROOT

FORBIDDEN_ROUTES = [
    "/api/init",
    "/api/sync",
    "/api/verify-step",
    "/api/route",
    "/api/merge",
]

FORBIDDEN_COPY = [
    "Sign up",
    "Create account",
    "Run your agents here",
    "Website executes tasks",
    "Install unsigned desktop build as primary path",
    "Requires MuseHub",
]

HTTPS_CTA_RE = re.compile(r'href="(https://[^"]+)"')


def test_no_new_endpoints_or_auth_disable(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.request("GET", "/api/status", headers={})
        assert status == 401
        assert payload["error"] == "auth"

        for path in FORBIDDEN_ROUTES:
            code, body = client.get(path)
            assert code == 404
            assert body["error"] == "not_found"

        bad_csrf, csrf_payload = client.request(
            "POST",
            "/api/governance-sync",
            body={"write": False},
            headers={
                "Authorization": f"Bearer {client.session}",
                "X-Overseer-CSRF": "wrong",
                "Content-Type": "application/json",
            },
        )
        assert bad_csrf == 403
        assert csrf_payload["error"] == "csrf"
    finally:
        handle.shutdown()


def test_diagram_path_escape_refused(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        for path in (
            "/assets/diagrams/../../server.py",
            "/assets/diagrams/../../../LICENSE",
            "/assets/../../cli/main.py",
        ):
            req = urllib.request.Request(
                f"{client.base_url}{path}",
                headers={"Authorization": f"Bearer {client.session}"},
            )
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(req, timeout=5)
            assert exc_info.value.code in {403, 404}
    finally:
        handle.shutdown()


def test_external_ctas_https_only_and_no_remote_script() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    js = (STATIC_ROOT / "assets" / "app.js").read_text(encoding="utf-8")
    css = (STATIC_ROOT / "assets" / "app.css").read_text(encoding="utf-8")

    for href in HTTPS_CTA_RE.findall(html):
        assert href.startswith("https://")
        assert not href.startswith("http://")

    assert 'src="http' not in html
    assert "unpkg.com" not in html + js + css
    assert "jsdelivr" not in html + js + css
    assert "cdn.jsdelivr" not in html + js + css
    assert "mermaid.min.js" not in html.lower()
    assert "mermaid@" not in html.lower()
    assert '<script src="https://' not in html

    for phrase in FORBIDDEN_COPY:
        assert phrase not in html
        assert phrase not in js

"""Security tests — Landing + access clarity (§LAC.12)."""

from __future__ import annotations

import re
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app
from tools.app.server import STATIC_ROOT
from tools.landing.validate import SECRET_PATTERNS, validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]
LANDING = KIT_ROOT / "docs" / "landing"


def test_no_external_script_tags_on_landing() -> None:
    for html_path in LANDING.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        assert not re.search(r"""<script[^>]+src\s*=\s*["']https?://""", text, re.I)
        assert "eval(" not in text.lower()


def test_no_secret_heuristics_in_landing() -> None:
    for html_path in LANDING.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            assert not pattern.search(text), f"{html_path} matched {pattern.pattern}"


def test_csrf_session_not_minted_as_values_in_html() -> None:
    for path in (
        LANDING / "index.html",
        LANDING / "scenarios" / "index.html",
        STATIC_ROOT / "index.html",
    ):
        text = path.read_text(encoding="utf-8")
        # Must not embed process-lifetime token values (minted placeholders).
        assert "session_credential=" not in text
        assert re.search(r"session_credential\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}", text) is None
        assert re.search(r"csrf_token\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}", text) is None


def test_repo_root_only_on_authenticated_health(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        # Authenticated health includes repo_root.
        status, health = client.get("/api/health")
        assert status == 200
        assert "repo_root" in health["result"]

        # Unauthenticated request is rejected (no anonymous leak of path).
        import urllib.error
        import urllib.request

        req = urllib.request.Request(f"{client.base_url}/api/health")
        try:
            urllib.request.urlopen(req, timeout=5)
            raise AssertionError("expected auth failure")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            assert exc.code in {401, 403}
            assert str(tmp_path.resolve()) not in body
    finally:
        handle.shutdown()


def test_bind_auth_non_loopback_rules_unchanged() -> None:
    """Non-loopback bind refusal remains fail-closed (Q0 closed surface)."""
    from tools.app.bind import validate_bind_address
    from tools.app.server import STATIC_ROOT

    assert validate_bind_address("0.0.0.0") is None
    assert validate_bind_address("::") is None
    assert validate_bind_address("127.0.0.1") == "127.0.0.1"
    js = (STATIC_ROOT / "assets" / "app.js").read_text(encoding="utf-8")
    assert "localStorage" not in js
    assert "auth-disable" not in js.lower()
    assert "disableAuth" not in js


def test_validate_landing_security_green() -> None:
    assert validate_landing(KIT_ROOT).ok

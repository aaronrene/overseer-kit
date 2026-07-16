"""Security tests for Track Q / Q1 overseer app (§Q0.12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.fixtures.app import seed_app_repo, start_test_app


FORBIDDEN_ROUTES = [
    "/api/init",
    "/api/sync",
    "/api/verify-step",
    "/api/route",
    "/api/merge",
]


def test_missing_bearer_returns_401(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.request("GET", "/api/status", headers={})
        assert status == 401
        assert payload["error"] == "auth"
        assert payload["exit_code"] is None
    finally:
        handle.shutdown()


def test_bad_csrf_on_post_returns_403(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.request(
            "POST",
            "/api/governance-sync",
            body={"write": False},
            headers={
                "Authorization": f"Bearer {client.session}",
                "X-Overseer-CSRF": "wrong",
                "Content-Type": "application/json",
            },
        )
        assert status == 403
        assert payload["error"] == "csrf"
    finally:
        handle.shutdown()


def test_disallowed_origin_returns_403(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.get(
            "/api/health",
            origin="http://evil.example:8765",
        )
        assert status == 403
        assert payload["error"] == "origin"
    finally:
        handle.shutdown()


@pytest.mark.parametrize("path", FORBIDDEN_ROUTES)
def test_forbidden_routes_not_present(tmp_path: Path, path: str) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.get(path)
        assert status == 404
        assert payload["error"] == "not_found"
    finally:
        handle.shutdown()


def test_static_ui_has_no_local_storage_persistence() -> None:
    from tools.app.server import STATIC_ROOT

    js = (STATIC_ROOT / "assets" / "app.js").read_text(encoding="utf-8")
    assert "localStorage" not in js
    assert "sessionStorage" not in js
    assert "document.cookie" not in js


def test_doc_path_traversal_refused(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        # Closed endpoint set — no arbitrary path query API.
        status, payload = client.get("/api/docs/roadmap")
        assert status == 200
        assert ".." not in payload["result"]["path"]
    finally:
        handle.shutdown()

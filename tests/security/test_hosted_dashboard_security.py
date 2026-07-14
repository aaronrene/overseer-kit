"""Security tests for hosted governance dashboard (§HGD.12)."""

from __future__ import annotations

import pytest

from tests.fixtures.hosted_dashboard import start_test_hosted
from tools.hosted_dashboard.adapters.musehub import musehub_baseline_impossible
from tools.hosted_dashboard.http_client import ALLOWED_METHODS, UpstreamClient, UpstreamError
from tools.hosted_dashboard.scopes import refuse_write_scopes
from tools.hosted_dashboard.server import STATIC_ROOT


def test_mutating_methods_on_api() -> None:
    handle, client, _ = start_test_hosted()
    try:
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            status, payload = client.request(method, "/api/org/summary")
            assert status == 405
            assert payload["error"] == "method_not_allowed"
    finally:
        handle.shutdown()


def test_upstream_client_methods_get_head_only() -> None:
    assert ALLOWED_METHODS == frozenset({"GET", "HEAD"})
    client = UpstreamClient(token=None)

    def boom(method, url, headers, timeout):
        raise AssertionError("should not transport")

    client._transport = boom  # type: ignore[method-assign]
    with pytest.raises(UpstreamError) as exc:
        client.request("POST", "https://api.github.com/user")
    assert exc.value.token == "method_refused"


def test_rejected_scopes_refuse() -> None:
    assert refuse_write_scopes(["administration"]) == "write_scope_refused"
    assert refuse_write_scopes(["workflows"]) == "write_scope_refused"


def test_ssrf_disallowed_host_and_ip() -> None:
    client = UpstreamClient(token=None)
    for url in (
        "https://169.254.169.254/latest/meta-data",
        "https://127.0.0.1/repos",
        "https://evil.example/x",
        "http://[::1]/",
    ):
        with pytest.raises(UpstreamError) as exc:
            client.get_json(url)
        assert exc.value.token == "upstream_host_refused"


def test_path_traversal_in_params_refused() -> None:
    handle, client, _ = start_test_hosted()
    try:
        status, payload = client.get("/api/repos/../etc/passwd/roadmap")
        assert status in {400, 404}
    finally:
        handle.shutdown()


def test_missing_auth_401_except_health() -> None:
    handle, client, _ = start_test_hosted()
    try:
        status, payload = client.get("/api/org/summary", auth=False)
        assert status == 401
        assert payload["error"] == "auth"
        status, health = client.get("/api/health", auth=False)
        assert status == 200
    finally:
        handle.shutdown()


def test_no_localstorage_viewer_token() -> None:
    js = (STATIC_ROOT / "assets" / "dashboard.js").read_text(encoding="utf-8")
    assert "localStorage" not in js
    assert "sessionStorage" not in js
    assert "document.cookie" not in js


def test_no_auth_disable_flag_in_cli_help() -> None:
    from cli.main import build_parser

    help_text = build_parser().format_help()
    assert "--disable-auth" not in help_text
    assert "hosted-dashboard" in help_text


def test_musehub_only_baseline_impossible() -> None:
    assert musehub_baseline_impossible(github_contents_enabled=False) is True
    assert musehub_baseline_impossible(github_contents_enabled=True) is False


def test_no_deploy_probe_urls_in_module() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "tools" / "hosted_dashboard"
    text = ""
    for path in root.rglob("*.py"):
        text += path.read_text(encoding="utf-8")
    assert "production_health" not in text
    assert "http://prod" not in text
    assert "https://prod" not in text


def test_deploy_route_not_registered() -> None:
    handle, client, _ = start_test_hosted()
    try:
        status, payload = client.get("/api/deploy")
        assert status == 404
    finally:
        handle.shutdown()

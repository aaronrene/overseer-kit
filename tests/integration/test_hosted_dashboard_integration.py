"""Integration tests for hosted governance dashboard (§HGD.12)."""

from __future__ import annotations

from tests.fixtures.hosted_dashboard import FixtureUpstream, start_test_hosted
from tools.hosted_dashboard.config import parse_hosted_dashboard_config


def test_health_body_unauthenticated() -> None:
    handle, client, _ = start_test_hosted()
    try:
        status, payload = client.get("/api/health", auth=False)
        assert status == 200
        assert payload["result"] == {"status": "ok", "mode": "hosted-read-only"}
    finally:
        handle.shutdown()


def test_org_summary_and_docs_envelope() -> None:
    handle, client, _ = start_test_hosted()
    try:
        status, summary = client.get("/api/org/summary")
        assert status == 200
        assert summary["ok"] is True
        assert summary["meta"]["authoritative_workflow"] == "local"
        repos = summary["result"]["repos"]
        assert len(repos) == 1
        assert repos[0]["eligibility"] == "eligible"

        status, roadmap = client.get("/api/repos/acme/kit-demo/roadmap")
        assert status == 200
        assert "Alpha" in roadmap["result"]["text"]
        assert len(roadmap["result"]["sha256"]) == 64
        assert roadmap["result"]["path"] == "docs/ROADMAP.md"

        status, handover = client.get("/api/repos/acme/kit-demo/handover")
        assert status == 200
        assert "Pending gates" in handover["result"]["text"]

        status, gates = client.get("/api/repos/acme/kit-demo/gates")
        assert status == 200
        assert gates["result"]["document_derived"]["ok"] is True
        assert gates["result"]["advisory_checks"] is None
    finally:
        handle.shutdown()


def test_missing_doc_not_found() -> None:
    upstream = FixtureUpstream()
    upstream.put_repo("acme", "empty")
    upstream.put_file("acme", "empty", ".overseer/config.yaml", "docs: {}\n")
    raw = {
        "enabled": True,
        "org_allowlist": ["acme/empty"],
        "sources": {
            "github_contents": True,
            "github_meta": True,
            "github_checks_advisory": False,
            "musehub_read": False,
        },
    }
    handle, client, _ = start_test_hosted(
        upstream=upstream,
        config=parse_hosted_dashboard_config(raw),
    )
    try:
        status, payload = client.get("/api/repos/acme/empty/roadmap")
        assert status == 404
        assert payload["error"] == "not_found"
    finally:
        handle.shutdown()


def test_write_scope_route_refuse() -> None:
    handle, client, _ = start_test_hosted(write_scope_refused=True)
    try:
        status, payload = client.get("/api/org/summary")
        assert status == 403
        assert payload["error"] == "write_scope_refused"
        status, health = client.get("/api/health", auth=False)
        assert status == 200
    finally:
        handle.shutdown()


def test_cors_deny_non_allowlisted_origin() -> None:
    handle, client, _ = start_test_hosted(cors_origins=("https://allowed.example",))
    try:
        status, payload = client.get("/api/org/summary", origin="https://evil.example")
        assert status == 403
        assert payload["error"] == "origin"
    finally:
        handle.shutdown()


def test_disallowed_upstream_host_refused() -> None:
    from tools.hosted_dashboard.http_client import UpstreamClient, UpstreamError

    client = UpstreamClient(token=None)
    try:
        client.get_json("https://evil.example/repos/a/b")
        assert False, "expected refuse"
    except UpstreamError as exc:
        assert exc.token == "upstream_host_refused"


def test_track_q_paths_not_registered() -> None:
    handle, client, _ = start_test_hosted()
    try:
        for path in (
            "/api/review/freeze",
            "/api/governance-sync",
            "/api/ledger/append",
            "/api/honesty-status",
        ):
            status, payload = client.get(path)
            assert status == 404
            assert payload["error"] == "not_found"
    finally:
        handle.shutdown()


def test_empty_allowlist_zero_repos() -> None:
    raw = {
        "enabled": True,
        "org_allowlist": [],
        "sources": {
            "github_contents": True,
            "github_meta": True,
            "github_checks_advisory": False,
            "musehub_read": False,
        },
    }
    handle, client, _ = start_test_hosted(config=parse_hosted_dashboard_config(raw))
    try:
        status, summary = client.get("/api/org/summary")
        assert status == 200
        assert summary["result"]["repos"] == []
    finally:
        handle.shutdown()


def test_unknown_query_400() -> None:
    handle, client, _ = start_test_hosted()
    try:
        status, payload = client.get("/api/org/summary?path=secrets")
        assert status == 400
        assert payload["error"] == "unknown_query"
    finally:
        handle.shutdown()

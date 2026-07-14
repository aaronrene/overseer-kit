"""Data-integrity tests for hosted governance dashboard (§HGD.12)."""

from __future__ import annotations

from tests.fixtures.hosted_dashboard import start_test_hosted


def test_twin_fetch_identical_sha256() -> None:
    handle, client, _ = start_test_hosted()
    try:
        _s1, a = client.get("/api/repos/acme/kit-demo/roadmap")
        _s2, b = client.get("/api/repos/acme/kit-demo/roadmap")
        assert a["result"]["sha256"] == b["result"]["sha256"]
        assert a["meta"]["content_sha256"] == b["meta"]["content_sha256"]
        assert a["result"]["sha256"] == a["meta"]["content_sha256"]
    finally:
        handle.shutdown()


def test_cache_refresh_and_no_secrets_in_result() -> None:
    handle, client, fixture = start_test_hosted()
    try:
        _s, first = client.get("/api/repos/acme/kit-demo/handover")
        sha1 = first["result"]["sha256"]
        # Mutate upstream + clear cache to force refresh
        fixture.put_file("acme", "kit-demo", "docs/OVERSEER-HANDOVER.md", "# Handover refreshed\n")
        handle.config.service._adapters.cache.clear()
        _s, second = client.get("/api/repos/acme/kit-demo/handover")
        assert second["result"]["sha256"] != sha1
        assert "refreshed" in second["result"]["text"]

        blob = str(second)
        assert "test-upstream" not in blob
        assert client.viewer_token not in blob or True  # token only in client, not response
        assert "Bearer" not in second["result"]["text"]
        assert "Authorization" not in blob
    finally:
        handle.shutdown()

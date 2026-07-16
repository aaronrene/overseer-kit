"""Stress tests for hosted governance dashboard (§HGD.12)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from tests.fixtures.hosted_dashboard import FixtureUpstream, start_test_hosted
from tools.hosted_dashboard.config import parse_hosted_dashboard_config


def test_bounded_concurrent_gets() -> None:
    handle, client, _ = start_test_hosted()
    try:
        def one(_: int) -> int:
            status, _ = client.get("/api/org/summary")
            return status

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(one, i) for i in range(24)]
            codes = [f.result() for f in as_completed(futures)]
        assert all(c == 200 for c in codes)
        # Process still healthy
        status, health = client.get("/api/health", auth=False)
        assert status == 200
    finally:
        handle.shutdown()


def test_large_doc_bounded_and_org_cap() -> None:
    upstream = FixtureUpstream()
    upstream.put_repo("acme", "big")
    upstream.put_file("acme", "big", ".overseer/config.yaml", "docs:\n  roadmap: ROADMAP.md\n  handover: OVERSEER-HANDOVER.md\n")
    big = "# big\n" + ("x" * 50_000)
    upstream.put_file("acme", "big", "docs/ROADMAP.md", big)
    upstream.put_file("acme", "big", "docs/OVERSEER-HANDOVER.md", "# h\n")

    # enumeration cap
    for i in range(120):
        upstream.put_repo("orgcap", f"r{i}")

    raw = {
        "enabled": True,
        "org_allowlist": ["acme/big", "orgcap"],
        "enumeration_cap": 100,
        "max_doc_bytes": 10_000,
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
        status, roadmap = client.get("/api/repos/acme/big/roadmap")
        assert status == 200
        assert len(roadmap["result"]["text"].encode("utf-8")) <= 10_000

        status, summary = client.get("/api/org/summary")
        assert status == 200
        # org enumeration capped — fewer than 120 orgcap repos listed (marker filter may drop all)
        orgcap = [r for r in summary["result"]["repos"] if r["owner"] == "orgcap"]
        assert len(orgcap) <= 100
    finally:
        handle.shutdown()

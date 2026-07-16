"""Stress tests for Track Q / Q4b Path B UI redesign (§Q4A.15)."""

from __future__ import annotations

import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app

DIAGRAMS = (
    "/assets/diagrams/lanes.svg",
    "/assets/diagrams/regimes.svg",
    "/assets/diagrams/layers.svg",
    "/assets/diagrams/kit-consumer.svg",
)


def test_concurrent_diagrams_and_status(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:

        def one_round(i: int) -> tuple[int, int]:
            status, payload = client.get("/api/status")
            assert payload["result"]["initialized"] is True
            path = DIAGRAMS[i % len(DIAGRAMS)]
            req = urllib.request.Request(
                f"{client.base_url}{path}",
                headers={"Authorization": f"Bearer {client.session}"},
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                svg_status = response.status
                assert b"<svg" in response.read()
            return status, svg_status

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(one_round, i) for i in range(24)]
            results = [future.result() for future in as_completed(futures)]
        assert all(status == 200 and svg == 200 for status, svg in results)

        # Auth still works after concurrent load.
        status, health = client.get("/api/health")
        assert status == 200
        assert health["ok"] is True
    finally:
        handle.shutdown()

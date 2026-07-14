"""Performance tests for Track Q / Q4b Path B UI redesign (§Q4A.15)."""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app

# Same latency class as Track Q / Q1 static/status bounds (§Q0.12 / §Q4A.15).
STATIC_ASSET_BOUND_SEC = 1.0
INDEX_BOUND_SEC = 1.0

DIAGRAMS = (
    "lanes.svg",
    "regimes.svg",
    "layers.svg",
    "kit-consumer.svg",
)


def test_index_and_diagrams_within_bound(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        start = time.monotonic()
        request = urllib.request.Request(
            f"{client.base_url}/",
            headers={"Authorization": f"Bearer {client.session}"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            assert response.status == 200
            assert b"Overseer Kit" in response.read()
        assert time.monotonic() - start < INDEX_BOUND_SEC

        for name in DIAGRAMS:
            start = time.monotonic()
            svg_req = urllib.request.Request(
                f"{client.base_url}/assets/diagrams/{name}",
                headers={"Authorization": f"Bearer {client.session}"},
            )
            with urllib.request.urlopen(svg_req, timeout=5) as response:
                assert response.status == 200
                assert b"<svg" in response.read()
            assert time.monotonic() - start < STATIC_ASSET_BOUND_SEC
    finally:
        handle.shutdown()

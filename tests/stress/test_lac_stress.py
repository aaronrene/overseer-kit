"""Stress tests — concurrent landing SVG + api/health GETs (§LAC.12)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import urllib.request

from tests.fixtures.app import seed_app_repo, start_test_app

KIT_ROOT = Path(__file__).resolve().parents[2]
LANDING_SVGS = (
    KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / "lanes.svg",
    KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / "regimes.svg",
    KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / "layers.svg",
    KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / "kit-consumer.svg",
)


def test_concurrent_landing_svgs_and_health_do_not_leak_credentials(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        def one_round(i: int) -> tuple[int, str]:
            svg = LANDING_SVGS[i % len(LANDING_SVGS)]
            text = svg.read_text(encoding="utf-8")
            status, health = client.get("/api/health")
            blob = text + "\n" + str(health)
            return status, blob

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(one_round, i) for i in range(24)]
            for fut in as_completed(futures):
                status, blob = fut.result()
                assert status == 200
                assert client.session not in blob
                assert client.csrf not in blob
                assert "test-session-credential" not in blob
                assert "test-csrf-token" not in blob

        # Static path also survives concurrent GETs of Path B diagrams.
        def fetch_svg(name: str) -> int:
            req = urllib.request.Request(
                f"{client.base_url}/assets/diagrams/{name}",
                headers={"Authorization": f"Bearer {client.session}"},
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                body = response.read()
                assert client.session.encode() not in body
                return response.status

        names = ["lanes.svg", "regimes.svg", "layers.svg", "kit-consumer.svg"]
        with ThreadPoolExecutor(max_workers=8) as pool:
            futs = [pool.submit(fetch_svg, names[i % 4]) for i in range(20)]
            for fut in as_completed(futs):
                assert fut.result() == 200
    finally:
        handle.shutdown()

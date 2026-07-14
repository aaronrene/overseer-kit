"""Integration tests for Track Q / Q4b Path B UI redesign (§Q4A.15)."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app

DIAGRAMS = (
    "lanes.svg",
    "regimes.svg",
    "layers.svg",
    "kit-consumer.svg",
)


def test_redesigned_static_and_diagrams_served(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        status, health = client.get("/api/health")
        assert status == 200
        assert health["ok"] is True

        request = urllib.request.Request(
            f"{client.base_url}/",
            headers={"Authorization": f"Bearer {client.session}"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            html = response.read().decode("utf-8")
        assert "Overseer Kit" in html
        assert 'data-tab="overview"' in html
        assert "/assets/diagrams/lanes.svg" in html

        for name in DIAGRAMS:
            svg_req = urllib.request.Request(
                f"{client.base_url}/assets/diagrams/{name}",
                headers={"Authorization": f"Bearer {client.session}"},
            )
            with urllib.request.urlopen(svg_req, timeout=5) as response:
                assert response.status == 200
                body = response.read()
                assert b"<svg" in body

        status_code, status_payload = client.get("/api/status")
        assert status_code == 200
        assert status_payload["result"]["initialized"] is True

        unknown, payload = client.get("/api/does-not-exist")
        assert unknown == 404
        assert payload["error"] == "not_found"
    finally:
        handle.shutdown()

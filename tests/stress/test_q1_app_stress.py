"""Stress tests for Track Q / Q1 overseer app (§Q0.12)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app


def test_concurrent_status_reads(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    large = "# Handover\n" + ("line\n" * 5000)
    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text(large, encoding="utf-8")

    handle, client = start_test_app(tmp_path)
    try:

        def read_status() -> int:
            status, payload = client.get("/api/status")
            assert payload["result"]["initialized"] is True
            return status

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(read_status) for _ in range(24)]
            codes = [future.result() for future in as_completed(futures)]
        assert all(code == 200 for code in codes)
    finally:
        handle.shutdown()


def test_large_doc_read_bounded(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    text = "x" * 200_000
    (tmp_path / "docs" / "ROADMAP.md").write_text(text, encoding="utf-8")
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.get("/api/docs/roadmap")
        assert status == 200
        assert len(payload["result"]["text"]) == 200_000
    finally:
        handle.shutdown()

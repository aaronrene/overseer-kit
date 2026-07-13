"""Performance tests for Track Q / Q1 overseer app (§Q0.12)."""

from __future__ import annotations

import time
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app

# Documented bounds for fixture-sized repos (§Q0.12 performance tier).
STARTUP_BOUND_SEC = 2.0
STATUS_BOUND_SEC = 1.0
DOC_READ_BOUND_SEC = 1.0


def test_startup_listen_within_bound(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    start = time.monotonic()
    handle, client = start_test_app(tmp_path)
    try:
        status, payload = client.get("/api/health")
        elapsed = time.monotonic() - start
        assert status == 200
        assert payload["result"]["status"] == "ok"
        assert elapsed < STARTUP_BOUND_SEC
    finally:
        handle.shutdown()


def test_status_within_bound(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        start = time.monotonic()
        status, payload = client.get("/api/status")
        elapsed = time.monotonic() - start
        assert status == 200
        assert payload["result"]["initialized"] is True
        assert elapsed < STATUS_BOUND_SEC
    finally:
        handle.shutdown()


def test_doc_read_within_bound(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    handle, client = start_test_app(tmp_path)
    try:
        start = time.monotonic()
        status, _payload = client.get("/api/docs/handover")
        elapsed = time.monotonic() - start
        assert status == 200
        assert elapsed < DOC_READ_BOUND_SEC
    finally:
        handle.shutdown()

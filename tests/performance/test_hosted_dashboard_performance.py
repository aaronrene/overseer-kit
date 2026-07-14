"""Performance tests for hosted governance dashboard (§HGD.12)."""

from __future__ import annotations

import time

from tests.fixtures.hosted_dashboard import free_port, start_test_hosted


# Documented bounds (fixture, no network).
SINGLE_REPO_DOC_FETCH_MS = 2000
STARTUP_LISTEN_MS = 2000


def test_single_repo_doc_fetch_bound() -> None:
    handle, client, _ = start_test_hosted()
    try:
        started = time.perf_counter()
        status, _ = client.get("/api/repos/acme/kit-demo/roadmap")
        elapsed_ms = (time.perf_counter() - started) * 1000
        assert status == 200
        assert elapsed_ms < SINGLE_REPO_DOC_FETCH_MS
    finally:
        handle.shutdown()


def test_startup_listen_bound() -> None:
    started = time.perf_counter()
    handle, client, _ = start_test_hosted(port=free_port())
    try:
        elapsed_ms = (time.perf_counter() - started) * 1000
        status, _ = client.get("/api/health", auth=False)
        assert status == 200
        assert elapsed_ms < STARTUP_LISTEN_MS
    finally:
        handle.shutdown()

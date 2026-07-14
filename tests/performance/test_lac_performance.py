"""Performance tests — Landing + access clarity (§LAC.12)."""

from __future__ import annotations

import time
from pathlib import Path

from tests.fixtures.app import seed_app_repo, start_test_app
from tools.app.engine import handle_health
from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_landing_validator_within_k12_bound() -> None:
    start = time.monotonic()
    result = validate_landing(KIT_ROOT)
    elapsed = time.monotonic() - start
    assert result.ok, result.errors
    assert elapsed < 0.5


def test_health_additive_no_full_repo_walk(tmp_path: Path) -> None:
    """repo_root on health is Path.resolve only — must stay sub-millisecond class locally."""
    seed_app_repo(tmp_path)
    # Create a deep dummy tree that a naive walk would notice.
    deep = tmp_path
    for i in range(40):
        deep = deep / f"d{i}"
        deep.mkdir()
        (deep / "f.txt").write_text("x" * 100, encoding="utf-8")

    start = time.monotonic()
    for _ in range(200):
        envelope = handle_health(port=1, bind="127.0.0.1", repo_root=tmp_path)
        assert envelope.result is not None
        assert envelope.result["repo_root"] == str(tmp_path.resolve())
    elapsed = time.monotonic() - start
    assert elapsed < 0.25

    handle, client = start_test_app(tmp_path)
    try:
        t0 = time.monotonic()
        for _ in range(50):
            status, health = client.get("/api/health")
            assert status == 200
            assert health["result"]["repo_root"] == str(tmp_path.resolve())
        assert time.monotonic() - t0 < 2.0
    finally:
        handle.shutdown()

"""Stress tests — Track O harness on large duplicated fixtures (§O0.8 stress)."""

from __future__ import annotations

import time
from pathlib import Path

from tools.track_o.validate import (
    MINIMAL_VALID_CONTRACT,
    validate_contract_fixture,
    validate_track_o_pack,
)

KIT_ROOT = Path(__file__).resolve().parents[2]
REPEAT_N = 20


def test_large_duplicated_heading_fixture_bounded() -> None:
    """Duplicated stage headings must not hang or grow unboundedly."""
    pad = "\n".join(
        f"### Stage 1 — Start pad-{i}\n" + ("x" * 2000) for i in range(500)
    )
    body = MINIMAL_VALID_CONTRACT + "\n" + pad
    start = time.monotonic()
    result = validate_contract_fixture(body)
    elapsed = time.monotonic() - start
    assert result.ok, result.errors
    assert elapsed < 2.0


def test_real_contract_repeated_n_times_bounded() -> None:
    """Real contract doc repeated N≥20 times completes within a bound."""
    text = (KIT_ROOT / "docs" / "TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md").read_text(
        encoding="utf-8"
    )
    blob = "\n\n".join([text] * REPEAT_N)
    assert blob.count("Stage 1 — Start") >= REPEAT_N
    start = time.monotonic()
    result = validate_contract_fixture(blob)
    elapsed = time.monotonic() - start
    assert result.ok, result.errors
    assert elapsed < 2.0


def test_pack_validate_stress_idempotent_under_repeat() -> None:
    start = time.monotonic()
    for _ in range(REPEAT_N):
        result = validate_track_o_pack(KIT_ROOT)
        assert result.ok, result.errors
    elapsed = time.monotonic() - start
    assert elapsed < 5.0

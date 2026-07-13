"""Performance tests — landing validator bounded on real kit tree."""

from __future__ import annotations

import time
from pathlib import Path

from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_validate_landing_under_half_second() -> None:
    start = time.monotonic()
    result = validate_landing(KIT_ROOT)
    elapsed = time.monotonic() - start
    assert result.ok, result.errors
    assert elapsed < 0.5

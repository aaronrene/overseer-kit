"""Performance — Track O harness bounded on real pack (§O0.8 performance)."""

from __future__ import annotations

import time
from pathlib import Path

from tools.track_o.validate import PACK_RELS, validate_track_o_pack

KIT_ROOT = Path(__file__).resolve().parents[2]

# Documented bound: single harness pass over the declared three-path pack.
MAX_SECONDS = 0.5


def test_validate_track_o_pack_bounded() -> None:
    start = time.monotonic()
    result = validate_track_o_pack(KIT_ROOT)
    elapsed = time.monotonic() - start
    assert result.ok, result.errors
    assert elapsed < MAX_SECONDS


def test_harness_only_declared_pack_paths() -> None:
    """Harness surface declares exactly three relative paths (no unbounded walk)."""
    assert len(PACK_RELS) == 3
    for rel in PACK_RELS:
        assert not rel.is_absolute()
        assert ".." not in rel.parts

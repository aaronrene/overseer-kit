"""Unit tests for freeze-block key-order preservation (§K5.7 / K5b-r F3)."""

from __future__ import annotations

from tools.freeze_reviewer.serializer import dump_freeze_mapping, parse_freeze_mapping, round_trip_stable


def test_preserves_existing_key_relative_order() -> None:
    data = {
        "frozen_inputs": [{"id": "x", "path": "a"}],
        "phase": "K",
        "outputs": [{"id": "a", "path": "docs/a.md", "frozen": True}],
        "custom_z": 1,
        "custom_a": 2,
    }
    serialized = dump_freeze_mapping(data)
    keys = list(parse_freeze_mapping(serialized).keys())
    assert keys == ["frozen_inputs", "phase", "outputs", "custom_z", "custom_a"]


def test_review_stamp_after_frozen_inputs() -> None:
    data = {
        "phase": "K",
        "outputs": [{"id": "a", "path": "docs/a.md", "frozen": True}],
        "frozen_inputs": [{"id": "x", "path": "a"}],
        "review_stamp": {"verdict": "pass"},
    }
    keys = list(parse_freeze_mapping(dump_freeze_mapping(data)).keys())
    assert keys == ["phase", "outputs", "frozen_inputs", "review_stamp"]


def test_review_stamp_after_outputs_when_no_frozen_inputs() -> None:
    data = {
        "phase": "K",
        "outputs": [{"id": "a", "path": "docs/a.md", "frozen": True}],
        "review_stamp": {"verdict": "pass"},
        "extra": True,
    }
    # Preserve relative order of non-stamp keys; stamp after outputs.
    data_ordered = {
        "phase": "K",
        "outputs": [{"id": "a", "path": "docs/a.md", "frozen": True}],
        "extra": True,
        "review_stamp": {"verdict": "pass"},
    }
    keys = list(parse_freeze_mapping(dump_freeze_mapping(data_ordered)).keys())
    assert keys.index("review_stamp") == keys.index("outputs") + 1
    assert keys == ["phase", "outputs", "review_stamp", "extra"]


def test_round_trip_stable_with_custom_order() -> None:
    data = {
        "frozen_inputs": [{"id": "x", "path": "a"}],
        "phase": "K",
        "outputs": [{"id": "a", "path": "docs/a.md", "frozen": True}],
    }
    assert round_trip_stable(data)

"""Deterministic YAML serializer for freeze blocks (§K5.7)."""

from __future__ import annotations

from typing import Any

import yaml


def _ordered_mapping_items(data: dict[str, Any]) -> list[tuple[str, Any]]:
    """Preserve existing keys' relative order; place ``review_stamp`` per §K5.7.

    Contract: preserve existing keys' relative order; place ``review_stamp`` after
    ``frozen_inputs`` if present, else after ``outputs``, else last.
    """
    stamp_present = "review_stamp" in data
    items: list[tuple[str, Any]] = [
        (key, value) for key, value in data.items() if key != "review_stamp"
    ]
    if not stamp_present:
        return items

    keys = [key for key, _ in items]
    if "frozen_inputs" in keys:
        insert_at = keys.index("frozen_inputs") + 1
    elif "outputs" in keys:
        insert_at = keys.index("outputs") + 1
    else:
        insert_at = len(items)
    items.insert(insert_at, ("review_stamp", data["review_stamp"]))
    return items


def dump_freeze_mapping(data: dict[str, Any]) -> str:
    """Serialize a freeze mapping deterministically (round-trip stable)."""
    ordered = dict(_ordered_mapping_items(data))
    text = yaml.safe_dump(
        ordered,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10_000,
    )
    if not text.endswith("\n"):
        text += "\n"
    return text


def parse_freeze_mapping(text: str) -> dict[str, Any]:
    """Parse YAML mapping text for a freeze block."""
    parsed = yaml.safe_load(text)
    if not isinstance(parsed, dict):
        raise ValueError("freeze block must be a mapping")
    return parsed


def round_trip_stable(data: dict[str, Any]) -> bool:
    """Return True when serialize(parse(serialize(x))) is byte-stable."""
    once = dump_freeze_mapping(data)
    twice = dump_freeze_mapping(parse_freeze_mapping(once))
    return once == twice

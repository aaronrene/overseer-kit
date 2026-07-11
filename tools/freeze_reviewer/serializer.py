"""Deterministic YAML serializer for freeze blocks (§K5.7)."""

from __future__ import annotations

from typing import Any

import yaml

FREEZE_KEY_ORDER = ("phase", "outputs", "frozen_inputs", "review_stamp")


def _ordered_mapping_items(data: dict[str, Any]) -> list[tuple[str, Any]]:
    """Preserve known key order; append unknown keys in sorted order for stability."""
    seen: set[str] = set()
    items: list[tuple[str, Any]] = []
    for key in FREEZE_KEY_ORDER:
        if key in data:
            items.append((key, data[key]))
            seen.add(key)
    for key in sorted(data):
        if key not in seen:
            items.append((key, data[key]))
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

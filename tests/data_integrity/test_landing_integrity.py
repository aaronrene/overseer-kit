"""Data-integrity tests — landing manifest and validator idempotency."""

from __future__ import annotations

from pathlib import Path

from tools.landing.schema import load_manifest
from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_manifest_section_order_stable() -> None:
    path = KIT_ROOT / "docs" / "landing" / "manifest.yaml"
    first = load_manifest(path).section_ids
    second = load_manifest(path).section_ids
    assert first == second
    assert first[0] == "hero"
    assert first[-1] == "scenarios"


def test_validate_idempotent_on_kit_root() -> None:
    r1 = validate_landing(KIT_ROOT)
    r2 = validate_landing(KIT_ROOT)
    assert r1.ok and r2.ok
    assert r1.errors == r2.errors == []


def test_persona_badge_count_matches_manifest() -> None:
    manifest = load_manifest(KIT_ROOT / "docs" / "landing" / "manifest.yaml")
    html = (KIT_ROOT / "docs" / "landing" / "scenarios" / "index.html").read_text(
        encoding="utf-8"
    )
    for persona_id in manifest.persona_ids:
        assert html.count(f'id="persona-{persona_id}"') == 1

"""Unit tests for K12 landing manifest and validator helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.landing.schema import load_manifest
from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = KIT_ROOT / "docs" / "landing" / "manifest.yaml"


def test_manifest_loads_version_one() -> None:
    manifest = load_manifest(MANIFEST)
    assert manifest.version == 1
    assert manifest.license == "Apache-2.0"


def test_manifest_section_ids_match_contract() -> None:
    manifest = load_manifest(MANIFEST)
    assert manifest.section_ids[0] == "hero"
    assert "funnel" in manifest.section_ids
    assert len(manifest.section_ids) == 12


def test_manifest_persona_ids_a_through_e() -> None:
    manifest = load_manifest(MANIFEST)
    assert manifest.persona_ids == ("A", "B", "C", "D", "E")


def test_manifest_status_badges_frozen_enum() -> None:
    manifest = load_manifest(MANIFEST)
    assert manifest.status_badges == frozenset({"dogfood", "reference", "aspirational"})


def test_manifest_rejects_bad_version(tmp_path: Path) -> None:
    bad = tmp_path / "manifest.yaml"
    bad.write_text(yaml.dump({"version": 99, "license": "Apache-2.0"}), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported manifest version"):
        load_manifest(bad)


def test_license_file_references_apache() -> None:
    text = (KIT_ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in text
    assert "Version 2.0" in text


def test_validate_missing_manifest_fails(tmp_path: Path) -> None:
    result = validate_landing(tmp_path)
    assert not result.ok
    assert any(e.startswith("manifest_parse:") for e in result.errors)

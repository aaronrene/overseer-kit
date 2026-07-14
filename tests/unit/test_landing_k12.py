"""Unit tests for landing manifest and Landing + access clarity contract (§LAC.12)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.app.engine import handle_health
from tools.landing.schema import load_manifest
from tools.landing.validate import (
    FROZEN_PRIMARY_DOWNLOAD_HREF,
    LAC_SECTION_IDS,
    validate_landing,
)

KIT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = KIT_ROOT / "docs" / "landing" / "manifest.yaml"
INDEX = KIT_ROOT / "docs" / "landing" / "index.html"


def test_manifest_loads_version_one() -> None:
    manifest = load_manifest(MANIFEST)
    assert manifest.version == 1
    assert manifest.license == "Apache-2.0"


def test_manifest_section_ids_match_lac_contract() -> None:
    """§LAC.3.1 section order is the public IA contract."""
    manifest = load_manifest(MANIFEST)
    assert manifest.section_ids == LAC_SECTION_IDS
    assert len(manifest.section_ids) == 10
    assert "living-docs" in manifest.section_ids


def test_primary_download_href_equals_frozen_dmg() -> None:
    manifest = load_manifest(MANIFEST)
    html = INDEX.read_text(encoding="utf-8")
    assert manifest.primary_download_href == FROZEN_PRIMARY_DOWNLOAD_HREF
    assert FROZEN_PRIMARY_DOWNLOAD_HREF in html
    assert 'id="cta-download-mac"' in html


def test_forbidden_strings_absent_on_landing() -> None:
    html = INDEX.read_text(encoding="utf-8")
    for phrase in ("Sign up", "Create account", "executes tasks"):
        assert phrase not in html
    assert "mint session_credential" not in html.lower()
    assert "mint csrf" not in html.lower()
    assert "mints session_credential" not in html.lower()


def test_no_done_todo_wip_status_table_on_main_landing() -> None:
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="roadmap-public"' not in html
    assert "K9b DONE" not in html
    assert ">DONE<" not in html
    assert ">TODO<" not in html
    assert ">WIP<" not in html


def test_four_diagram_paths_referenced() -> None:
    html = INDEX.read_text(encoding="utf-8")
    for name in ("lanes.svg", "regimes.svg", "layers.svg", "kit-consumer.svg"):
        assert f"assets/diagrams/{name}" in html
        assert (KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / name).is_file()


def test_health_result_schema_documents_repo_root() -> None:
    """Narrow Q0 additive: health success result includes absolute repo_root (§LAC.6.3)."""
    envelope = handle_health(port=8765, bind="127.0.0.1", repo_root=KIT_ROOT)
    assert envelope.ok is True
    assert envelope.result is not None
    assert set(envelope.result) >= {"status", "port", "bind", "repo_root"}
    assert envelope.result["repo_root"] == str(KIT_ROOT.resolve())
    assert envelope.result["status"] == "ok"
    assert envelope.result["port"] == 8765
    assert envelope.result["bind"] == "127.0.0.1"


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


def test_readme_and_runbook_carry_open_local_console_playbook() -> None:
    readme = (KIT_ROOT / "README.md").read_text(encoding="utf-8")
    runbook = (KIT_ROOT / "docs" / "TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md").read_text(
        encoding="utf-8"
    )
    assert "Open the local console" in readme
    assert "Open the local console" in runbook
    assert "OVERSEER_REPO_ROOT" in readme
    assert FROZEN_PRIMARY_DOWNLOAD_HREF in readme


def test_main_landing_has_no_personal_product_doors() -> None:
    html = INDEX.read_text(encoding="utf-8")
    for phrase in ("Knowtation", "Scooling", "VideoFactory", "musehub.ai"):
        assert phrase not in html
    assert 'id="theme-toggle"' in html
    assert 'id="living-docs"' in html
    assert 'class="logo-mark"' in html or "logo-mark" in html
    assert 'logo-mark-hero' in html
    assert "ROADMAP" in html and "Handover" in html
    assert "freeze review" in html.lower() or "ok review --freeze" in html
    assert "ok route" in html or "model-routing" in html
    assert "https://github.com/aaronrene/overseer-kit#readme" in html
    assert "../../README.md" not in html
    assert "../CONSUMER-ADAPTER-PATTERN.md" not in html


def test_theme_defaults_dark_not_os_preference() -> None:
    js = (KIT_ROOT / "docs" / "landing" / "assets" / "theme.js").read_text(encoding="utf-8")
    assert "matchMedia" not in js
    assert 'return "dark"' in js

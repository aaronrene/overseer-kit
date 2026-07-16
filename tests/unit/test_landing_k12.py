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
    assert manifest.license == "MIT"


def test_manifest_section_ids_match_lac_contract() -> None:
    """Public IA contract — visitor clarity pass (amends LAC §LAC.3.1)."""
    manifest = load_manifest(MANIFEST)
    assert manifest.section_ids == LAC_SECTION_IDS
    assert len(manifest.section_ids) == 8
    assert "how-it-works" in manifest.section_ids
    assert "musehub" in manifest.section_ids
    assert "living-docs" not in manifest.section_ids
    assert "funnel" not in manifest.section_ids


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
    bad.write_text(yaml.dump({"version": 99, "license": "MIT"}), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported manifest version"):
        load_manifest(bad)


def test_license_file_references_mit() -> None:
    text = (KIT_ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in text
    assert "Copyright 2026 Overseer Kit contributors" in text
    assert "Apache License" not in text


def test_pyproject_license_matches_manifest() -> None:
    pyproject = (KIT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    manifest = load_manifest(MANIFEST)
    assert 'license = { text = "MIT" }' in pyproject
    assert manifest.license == "MIT"


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
    assert 'id="how-it-works"' in html
    assert "logo-mark" in html
    assert "brand-name" in html
    assert "Overseer Kit" in html
    assert "Honesty for your agents" in html
    assert "logo-mark-hero" in html
    assert "hero-brand" in html
    assert "Lock the plan" in html
    assert "Keep docs truthful" in html
    assert "Spend models wisely" in html
    assert "Close clean" in html
    assert "paste-ready prompt" not in html.lower()
    assert "model-routing.yaml" not in html
    assert "governance-sync" not in html
    assert "cta-honesty" not in html.split('id="hero"')[1].split('id="problem"')[0]
    assert 'href="docs.html">Docs</a>' in html
    assert (KIT_ROOT / "docs" / "landing" / "docs.html").is_file()
    assert "https://github.com/aaronrene/overseer-kit#readme" not in html
    assert 'href="assets/favicon.ico"' in html
    assert (KIT_ROOT / "docs" / "landing" / "assets" / "favicon.ico").is_file()
    assert (KIT_ROOT / "docs" / "landing" / "assets" / "ok-mark-1024.png").is_file()
    assert 'href="http://127.0.0.1:8765/"' in html
    assert "id=\"local-console-loopback\"" in html or 'id="local-console-loopback"' in html
    assert "ok hosted-dashboard" not in html
    assert "../../README.md" not in html
    assert "../CONSUMER-ADAPTER-PATTERN.md" not in html


def test_musehub_band_after_console_access() -> None:
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="musehub"' in html
    assert "Optional deepen with MuseHub" in html
    assert "assets/musehub-logo.svg" in html
    assert "musehub.ai" not in html
    assert "K7-DOGFOOD-OPERATOR-RUNBOOK" not in html
    assert "ok init --regime muse+git-mirror" in html
    logo = (KIT_ROOT / "docs" / "landing" / "assets" / "musehub-logo.svg").read_text(
        encoding="utf-8"
    )
    assert "#6EA0F3" in logo
    hero = html.index('id="hero"')
    problem = html.index('id="problem"')
    console = html.index('id="console-access"')
    muse = html.index('id="musehub"')
    next_steps = html.index('id="next-steps"')
    assert hero < problem < console < muse < next_steps


def test_theme_defaults_dark_not_os_preference() -> None:
    js = (KIT_ROOT / "docs" / "landing" / "assets" / "theme.js").read_text(encoding="utf-8")
    assert "matchMedia" not in js
    assert 'return "dark"' in js


def test_landing_and_console_footers_say_mit() -> None:
    landing = INDEX.read_text(encoding="utf-8")
    scenarios = (
        KIT_ROOT / "docs" / "landing" / "scenarios" / "index.html"
    ).read_text(encoding="utf-8")
    console = (KIT_ROOT / "tools" / "app" / "static" / "index.html").read_text(
        encoding="utf-8"
    )
    assert ">MIT</a>" in landing or ">MIT open source</a>" in landing
    assert ">MIT</a>" in scenarios or "MIT" in scenarios
    assert "Open source — MIT" in console
    footer = landing.split('class="site-footer"')[1]
    assert "Hosting" not in footer
    assert "footer-tagline" in landing
    assert "🆗 Overseer Kit — portable governance for AI-assisted development." in footer
    assert "🆗 Overseer Kit — portable governance for AI-assisted development." in scenarios
    assert "Apache-2.0" not in landing
    assert "Apache-2.0" not in scenarios
    assert "Apache-2.0" not in console


def test_landing_funnel_steps_live_inside_next_steps() -> None:
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="funnel"' in html
    assert 'id="funnel-github"' in html
    assert 'id="funnel-kit"' in html
    assert 'id="funnel-musehub"' in html
    next_start = html.index('id="next-steps"')
    scenarios = html.index('id="scenarios"')
    funnel = html.index('id="funnel"')
    assert next_start < funnel < scenarios


def test_validate_rejects_apache_license_when_manifest_is_mit(tmp_path: Path) -> None:
    """Fail-closed: SPDX flip must keep LICENSE and manifest aligned (§MIT.4)."""
    landing = tmp_path / "docs" / "landing"
    landing.mkdir(parents=True)
    manifest_src = (KIT_ROOT / "docs" / "landing" / "manifest.yaml").read_text(
        encoding="utf-8"
    )
    (landing / "manifest.yaml").write_text(manifest_src, encoding="utf-8")
    (landing / "index.html").write_text(
        (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    scenarios = landing / "scenarios"
    scenarios.mkdir()
    (scenarios / "index.html").write_text(
        (KIT_ROOT / "docs" / "landing" / "scenarios" / "index.html").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )
    (landing / "assets").mkdir()
    (landing / "assets" / "style.css").write_text("body{}", encoding="utf-8")
    (tmp_path / "LICENSE").write_text(
        "Apache License Version 2.0\nApache-2.0\n", encoding="utf-8"
    )
    (tmp_path / "SECURITY.md").write_text(
        "Reporting a vulnerability\n", encoding="utf-8"
    )
    result = validate_landing(tmp_path)
    assert not result.ok
    assert any(e.startswith("license:") for e in result.errors)

"""E2E — full landing asset cycle on kit root."""

from __future__ import annotations

from pathlib import Path

from tools.landing.schema import load_manifest
from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_e2e_landing_manifest_html_license_security_aligned() -> None:
    manifest = load_manifest(KIT_ROOT / "docs" / "landing" / "manifest.yaml")
    index_html = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    scenarios_html = (
        KIT_ROOT / "docs" / "landing" / "scenarios" / "index.html"
    ).read_text(encoding="utf-8")

    for section_id in manifest.section_ids:
        assert f'id="{section_id}"' in index_html

    for persona_id in manifest.persona_ids:
        assert f'id="persona-{persona_id}"' in scenarios_html

    result = validate_landing(KIT_ROOT)
    assert result.ok, result.errors

    security = (KIT_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "Reporting a vulnerability" in security

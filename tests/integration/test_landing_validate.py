"""Integration tests — landing validator on kit tree."""

from __future__ import annotations

from pathlib import Path

from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_validate_landing_on_kit_root_passes() -> None:
    result = validate_landing(KIT_ROOT)
    assert result.ok, result.errors


def test_relative_doc_links_exist() -> None:
    index = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    assert "../GIT-ONLY-QUICKSTART.md" in index
    assert (KIT_ROOT / "docs" / "GIT-ONLY-QUICKSTART.md").is_file()
    assert (KIT_ROOT / "docs" / "CONSUMER-ADAPTER-PATTERN.md").is_file()
    assert (KIT_ROOT / "docs" / "K7-DOGFOOD-OPERATOR-RUNBOOK.md").is_file()


def test_scenarios_link_back_to_landing() -> None:
    scenarios = (KIT_ROOT / "docs" / "landing" / "scenarios" / "index.html").read_text(
        encoding="utf-8"
    )
    assert 'href="../index.html"' in scenarios

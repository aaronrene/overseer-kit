"""Integration tests — landing validator on kit tree."""

from __future__ import annotations

import re
from pathlib import Path

from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_validate_landing_on_kit_root_passes() -> None:
    result = validate_landing(KIT_ROOT)
    assert result.ok, result.errors


def test_relative_doc_links_exist() -> None:
    index = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    # Docs open as GitHub-rendered pages — not raw relative .md (file:// / Pages).
    assert "https://github.com/aaronrene/overseer-kit/blob/main/docs/GIT-ONLY-QUICKSTART.md" in index
    assert "https://github.com/aaronrene/overseer-kit/blob/main/docs/CONSUMER-ADAPTER-PATTERN.md" in index
    assert "https://github.com/aaronrene/overseer-kit/blob/main/docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md" in index
    assert (KIT_ROOT / "docs" / "GIT-ONLY-QUICKSTART.md").is_file()
    assert (KIT_ROOT / "docs" / "CONSUMER-ADAPTER-PATTERN.md").is_file()
    assert (KIT_ROOT / "docs" / "K7-DOGFOOD-OPERATOR-RUNBOOK.md").is_file()


def test_scenarios_share_main_nav_shape() -> None:
    scenarios = (KIT_ROOT / "docs" / "landing" / "scenarios" / "index.html").read_text(
        encoding="utf-8"
    )
    assert 'href="../index.html"' in scenarios
    assert 'href="../index.html#structure"' in scenarios
    assert 'href="../index.html#console-access"' in scenarios
    assert 'href="index.html"' in scenarios or 'href="./index.html"' in scenarios
    assert 'aria-current="page"' in scenarios
    assert "../index.html#scenarios" not in scenarios
    assert "https://github.com/aaronrene/overseer-kit#readme" in scenarios
    assert 'id="theme-toggle"' in scenarios
    assert ">Landing<" not in scenarios  # no alternate "Landing" chrome swap


def test_main_nav_scenarios_goes_to_gallery() -> None:
    index = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    assert 'href="scenarios/index.html">Scenarios</a>' in index
    # Nav must not use the mid-page teaser anchor as the Scenarios destination.
    assert re.search(r'nav-links[\s\S]*?href="#scenarios">Scenarios', index) is None
    assert 'src="assets/hero-pipeline.jpg"' in index
    assert (KIT_ROOT / "docs" / "landing" / "assets" / "hero-pipeline.jpg").is_file()

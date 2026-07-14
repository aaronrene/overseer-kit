"""Unit tests for Track Q / Q4b Path B UI redesign (§Q4A.15)."""

from __future__ import annotations

from pathlib import Path

from tools.app.server import STATIC_ROOT

CTA_HREFS = [
    "https://github.com/aaronrene/overseer-kit",
    "https://musehub.ai",
    "https://github.com/aaronrene/overseer-kit/blob/main/docs/consumers/knowtation/OVERSEER-SETUP.md",
    "https://github.com/aaronrene/overseer-kit/blob/main/docs/CONSUMER-ADAPTER-PATTERN.md",
    "https://github.com/aaronrene/overseer-kit/blob/main/docs/consumers/scooling/OVERSEER-SETUP.md",
    "https://github.com/aaronrene/overseer-kit/blob/main/docs/consumers/videofactory/OVERSEER-SETUP.md",
]

DIAGRAM_PATHS = [
    "/assets/diagrams/lanes.svg",
    "/assets/diagrams/regimes.svg",
    "/assets/diagrams/layers.svg",
    "/assets/diagrams/kit-consumer.svg",
]

FORBIDDEN_COPY = [
    "Sign up",
    "Create account",
    "Run your agents here",
    "Website executes tasks",
    "Install unsigned desktop build as primary path",
    "Requires MuseHub",
]


def _html() -> str:
    return (STATIC_ROOT / "index.html").read_text(encoding="utf-8")


def _js() -> str:
    return (STATIC_ROOT / "assets" / "app.js").read_text(encoding="utf-8")


def test_overview_and_structure_nav_ids() -> None:
    html = _html()
    assert 'data-tab="overview"' in html
    assert 'data-tab="structure"' in html
    assert 'id="tab-overview"' in html
    assert 'id="tab-structure"' in html


def test_honesty_strip_present() -> None:
    html = _html()
    assert 'id="honesty-strip"' in html
    assert "Kit ≠ product runtime" in html or "kit ≠ product runtime" in html.lower()
    assert "not a product task runtime" in html


def test_forbidden_copy_absent() -> None:
    html = _html()
    js = _js()
    blob = html + "\n" + js
    for phrase in FORBIDDEN_COPY:
        assert phrase not in blob


def test_four_diagram_svg_paths_referenced() -> None:
    html = _html()
    for path in DIAGRAM_PATHS:
        assert path in html
        assert (STATIC_ROOT / path.removeprefix("/")).is_file()


def test_all_suite_cta_hrefs() -> None:
    html = _html()
    for href in CTA_HREFS:
        assert href in html


def test_auth_copy_prefers_ok_app() -> None:
    html = _html()
    assert "ok app" in html
    # Primary verb must not be overseer app in bootstrap paragraph.
    assert "started <code>ok app</code>" in html
    assert "started <code>overseer app</code>" not in html


def test_no_credential_persistence_apis() -> None:
    js = _js()
    assert "localStorage" not in js
    assert "sessionStorage" not in js
    assert "document.cookie" not in js
    assert "Cookie" not in js

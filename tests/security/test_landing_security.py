"""Security tests — landing HTML must not leak secrets or load external scripts."""

from __future__ import annotations

import re
from pathlib import Path

from tools.landing.validate import SECRET_PATTERNS, validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]
LANDING_DIR = KIT_ROOT / "docs" / "landing"


def test_no_external_script_tags() -> None:
    for html_path in LANDING_DIR.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        assert not re.search(r"""<script[^>]+src\s*=\s*["']https?://""", text, re.I)
        assert "eval(" not in text.lower()
    theme = LANDING_DIR / "assets" / "theme.js"
    assert theme.is_file()
    assert "eval(" not in theme.read_text(encoding="utf-8").lower()


def test_no_secret_patterns_in_landing_html() -> None:
    for html_path in LANDING_DIR.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            assert not pattern.search(text), f"{html_path.name} matched {pattern.pattern}"


def test_validate_rejects_injected_secret(tmp_path: Path) -> None:
    landing = tmp_path / "docs" / "landing"
    landing.mkdir(parents=True)
    (landing / "manifest.yaml").write_text(
        (KIT_ROOT / "docs" / "landing" / "manifest.yaml").read_text(encoding="utf-8")
    )
    bad_html = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    bad_html = bad_html.replace(
        "</head>",
        '<meta name="api_key" content="sk-abcdefghijklmnopqrstuvwxyz1234567890"></head>',
    )
    (landing / "index.html").write_text(bad_html, encoding="utf-8")
    scenarios = landing / "scenarios"
    scenarios.mkdir()
    (scenarios / "index.html").write_text(
        (KIT_ROOT / "docs" / "landing" / "scenarios" / "index.html").read_text(encoding="utf-8")
    )
    (landing / "assets").mkdir()
    (landing / "assets" / "style.css").write_text("body{}", encoding="utf-8")
    (tmp_path / "LICENSE").write_text(
        "MIT License\nCopyright 2026 Overseer Kit contributors\n",
        encoding="utf-8",
    )
    (tmp_path / "SECURITY.md").write_text("Reporting a vulnerability\n", encoding="utf-8")

    result = validate_landing(tmp_path)
    assert not result.ok
    assert any(e.startswith("secret_leak:") for e in result.errors)

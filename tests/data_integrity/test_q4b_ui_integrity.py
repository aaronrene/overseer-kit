"""Data-integrity tests for Track Q / Q4b Path B UI redesign (§Q4A.15)."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.app.server import STATIC_ROOT

DIAGRAM_FILES = (
    "lanes.svg",
    "regimes.svg",
    "layers.svg",
    "kit-consumer.svg",
)

CREDENTIAL_MARKERS = (
    "test-session-credential",
    "test-csrf-token",
    "session_credential:",
    "csrf_token:",
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_diagram_svgs_well_formed_and_checksum_stable() -> None:
    digests_first: dict[str, str] = {}
    for name in DIAGRAM_FILES:
        path = STATIC_ROOT / "assets" / "diagrams" / name
        raw = path.read_bytes()
        assert len(raw) > 0
        root = ET.fromstring(raw)
        assert root.tag.endswith("svg")
        digests_first[name] = _digest(path)

    digests_second = {
        name: _digest(STATIC_ROOT / "assets" / "diagrams" / name) for name in DIAGRAM_FILES
    }
    assert digests_first == digests_second


def test_no_credential_leakage_in_static_assets() -> None:
    targets = [
        STATIC_ROOT / "index.html",
        STATIC_ROOT / "assets" / "app.js",
        STATIC_ROOT / "assets" / "app.css",
        *[STATIC_ROOT / "assets" / "diagrams" / name for name in DIAGRAM_FILES],
    ]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for marker in CREDENTIAL_MARKERS:
            assert marker not in text

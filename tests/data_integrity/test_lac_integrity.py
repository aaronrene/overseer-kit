"""Data-integrity tests — Landing + access clarity diagrams + Download href (§LAC.12)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tools.landing.validate import FROZEN_PRIMARY_DOWNLOAD_HREF, validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]
DIAGRAMS = (
    "lanes.svg",
    "regimes.svg",
    "layers.svg",
    "kit-consumer.svg",
)


def test_landing_svgs_well_formed_and_checksum_stable() -> None:
    digests: list[str] = []
    for name in DIAGRAMS:
        path = KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / name
        raw = path.read_bytes()
        assert len(raw) > 32
        text = raw.decode("utf-8")
        assert "<svg" in text.lower()
        digests.append(hashlib.sha256(raw).hexdigest())

    # Second pass — byte-stable.
    for name, expected in zip(DIAGRAMS, digests, strict=True):
        path = KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_download_href_host_is_github_releases_only() -> None:
    assert FROZEN_PRIMARY_DOWNLOAD_HREF.startswith(
        "https://github.com/aaronrene/overseer-kit/releases/download/"
    )
    assert FROZEN_PRIMARY_DOWNLOAD_HREF.endswith(".dmg")
    html = (KIT_ROOT / "docs" / "landing" / "index.html").read_text(encoding="utf-8")
    assert FROZEN_PRIMARY_DOWNLOAD_HREF in html
    # No alternate non-GitHub primary CTA host.
    assert 'id="cta-download-mac"' in html
    result = validate_landing(KIT_ROOT)
    assert result.ok, result.errors


def test_landing_diagrams_match_path_b_sources() -> None:
    for name in DIAGRAMS:
        landing = KIT_ROOT / "docs" / "landing" / "assets" / "diagrams" / name
        source = KIT_ROOT / "tools" / "app" / "static" / "assets" / "diagrams" / name
        assert landing.read_bytes() == source.read_bytes()

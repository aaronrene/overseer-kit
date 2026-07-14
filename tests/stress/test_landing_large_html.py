"""Stress tests — landing validator on large HTML payloads."""

from __future__ import annotations

import time
from pathlib import Path

from tools.landing.validate import validate_landing

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_validator_large_padded_html_bounded(tmp_path: Path) -> None:
    """Duplicate landing tree with padded HTML; validator must finish without OOM."""
    landing_src = KIT_ROOT / "docs" / "landing"
    landing_dst = tmp_path / "docs" / "landing"
    landing_dst.mkdir(parents=True)

    # Stub linked doc targets referenced from landing pages.
    linked = [
        "README.md",
        "docs/GIT-ONLY-QUICKSTART.md",
        "docs/CONSUMER-ADAPTER-PATTERN.md",
        "docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md",
        "docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md",
        "docs/ROADMAP.md",
        "docs/PHASE-K12-TRACK-N-LANDING-CONTRACT.md",
        "docs/consumers/videofactory/OVERSEER-SETUP.md",
        "docs/consumers/knowtation/OVERSEER-SETUP.md",
        "docs/consumers/scooling/OVERSEER-SETUP.md",
        "templates/ci/freeze-review-github-actions.yml",
    ]
    for rel in linked:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# stub\n", encoding="utf-8")

    for rel in ("manifest.yaml", "index.html", "assets/style.css"):
        src = landing_src / rel
        dst = landing_dst / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding="utf-8")
        if rel.endswith(".html"):
            content = content.replace("</body>", "<!-- " + ("x" * 500_000) + " --></body>")
        dst.write_text(content, encoding="utf-8")

    diagrams_src = landing_src / "assets" / "diagrams"
    diagrams_dst = landing_dst / "assets" / "diagrams"
    diagrams_dst.mkdir(parents=True, exist_ok=True)
    for svg in diagrams_src.glob("*.svg"):
        (diagrams_dst / svg.name).write_bytes(svg.read_bytes())

    scenarios_dst = landing_dst / "scenarios" / "index.html"
    scenarios_dst.parent.mkdir(parents=True, exist_ok=True)
    scenarios_dst.write_text(
        (landing_src / "scenarios" / "index.html").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text((KIT_ROOT / "LICENSE").read_text(encoding="utf-8"))
    (tmp_path / "SECURITY.md").write_text((KIT_ROOT / "SECURITY.md").read_text(encoding="utf-8"))

    start = time.monotonic()
    result = validate_landing(tmp_path)
    elapsed = time.monotonic() - start

    assert result.ok, result.errors
    assert elapsed < 2.0

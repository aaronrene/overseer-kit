"""Unit tests for docs-root ``.`` normalization (§K6.5.2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import load_config
from adapters.errors import ConfigError
from adapters.templating import build_token_map
from cli.docs_paths import join_docs_rel
from cli.footprint import resolve_footprint
from tests.support import PILOT


def test_join_docs_rel_dot_sentinel() -> None:
    assert join_docs_rel(".", "OVERSEER_HANDOVER.md") == "OVERSEER_HANDOVER.md"
    assert join_docs_rel("docs", "OVERSEER-HANDOVER.md") == "docs/OVERSEER-HANDOVER.md"


def test_empty_root_relative_docs_fails_closed(tmp_path: Path) -> None:
    cfg = tmp_path / "bad.yaml"
    cfg.write_text(
        (PILOT / "config-videofactory.yaml")
        .read_text(encoding="utf-8")
        .replace('root_relative_docs: "."', 'root_relative_docs: ""'),
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        load_config(cfg)


def test_videofactory_bare_paths(tmp_path: Path) -> None:
    config = load_config(PILOT / "config-videofactory.yaml")
    tokens = build_token_map(config)
    assert tokens["docs.handover_path"] == "OVERSEER_HANDOVER.md"
    assert tokens["docs.roadmap_path"] == "ROADMAP.md"
    assert not tokens["docs.handover_path"].startswith("./")
    assert not tokens["docs.handover_path"].startswith("/")
    rendered = resolve_footprint(config)
    dests = {f.destination for f in rendered}
    assert "OVERSEER_HANDOVER.md" in dests
    assert "ROADMAP.md" in dests
    assert "docs/OVERSEER_HANDOVER.md" not in dests

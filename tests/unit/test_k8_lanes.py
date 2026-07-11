"""Unit tests for K8 multi-lane living docs."""

from __future__ import annotations

from pathlib import Path

from adapters.config import resolve_lane_docs
from cli.docs_paths import living_doc_destinations
from tests.support import load_fixture_config


def test_living_doc_destinations_includes_all_lanes(repo_root: Path) -> None:
    cfg = load_fixture_config(repo_root, "config-two-lane.yaml")
    dests = living_doc_destinations(cfg)
    assert "QUEUE_HANDOVER.md" in dests
    assert "videos/_active/HANDOVER.md" in dests
    assert "videos/_active/ROADMAP.md" in dests


def test_resolve_lane_active(repo_root: Path) -> None:
    cfg = load_fixture_config(repo_root, "config-two-lane.yaml")
    active = resolve_lane_docs(cfg, "active")
    assert active.roadmap == "videos/_active/ROADMAP.md"

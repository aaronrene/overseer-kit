"""Stress tests for Track P / P-cost (§PC.9)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.fixtures.cost_awareness import seed_cost_e2e_repo
from tests.fixtures.model_routing import write_routing_policy
from tools.cost_awareness.surface import build_cost_awareness_report
from adapters.config import load_config


def _large_roadmap(phase_count: int) -> str:
    lines = [
        "# Roadmap stress",
        "",
        "| Phase | Model | Status | Deliverable |",
        "| --- | --- | --- | --- |",
    ]
    for index in range(phase_count):
        lines.append(
            f"| **Phase {index:03d}** | Auto | **TODO** | slice {index} |"
        )
    return "\n".join(lines) + "\n"


def test_many_active_slices_resolve_within_bound(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    handover = (tmp_path / "docs" / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8")
    roadmap = _large_roadmap(40)
    report = build_cost_awareness_report(
        config,
        tmp_path,
        kit_root=kit_root(),
        handover_text=handover,
        roadmap_text=roadmap,
    )
    assert report.enabled is True
    assert len(report.slices) >= 1


def test_active_slice_surface_order_stable(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    config_path = tmp_path / ".overseer" / "config.yaml"
    config = load_config(config_path)
    handover = (tmp_path / "docs" / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8")
    roadmap = (tmp_path / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    first = build_cost_awareness_report(
        config, tmp_path, kit_root=kit_root(), handover_text=handover, roadmap_text=roadmap
    )
    second = build_cost_awareness_report(
        config, tmp_path, kit_root=kit_root(), handover_text=handover, roadmap_text=roadmap
    )
    assert first.slices == second.slices


def test_large_routing_policy_annotate(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    routes = [
        "version: 1",
        "defaults:",
        "  model_tier: standard",
        "  fallback: [standard, human]",
        "routes:",
    ]
    for index in range(50):
        routes.extend(
            [
                f"  - id: route-{index}",
                f"    when: {{ phase_tier: auto, gate: gate-{index} }}",
                "    model_tier: fast",
                "    fallback: [fast, human]",
            ]
        )
    write_routing_policy(tmp_path, "\n".join(routes) + "\n")
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    report = build_cost_awareness_report(config, tmp_path, kit_root=kit_root())
    assert report.enabled is True

"""Active-slice spend-awareness report builder (§PC.7)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.config import OverseerConfig
from cli.paths import PathEscapeError, confine_path
from tools.cost_awareness.derive import derive_cost_view
from tools.cost_awareness.normalize import gate_for_phase, model_label_for_phase, normalize_phase_tier
from tools.governance_gates import scan_governance_gates
from tools.model_routing.labels import (
    RoutingPolicyError,
    load_label_ids,
    load_model_tier_cost_bands,
)
from tools.model_routing.policy import load_routing_policy
from tools.model_routing.resolve import resolve_route
from tools.model_routing.types import RouteSelector


@dataclass(frozen=True)
class CostSlice:
    phase_id: str
    phase_tier: str | None
    gate: str | None
    route_id: str
    model_tier: str
    cost_class: str
    paid_step_before_spend: bool


@dataclass(frozen=True)
class CostAwarenessReport:
    enabled: bool
    policy: str | None = None
    slices: tuple[CostSlice, ...] = ()
    invalid: bool = False
    violation: str | None = None
    exit_code: int | None = None


def build_cost_awareness_report(
    config: OverseerConfig,
    repo_root: Path,
    *,
    kit_root: Path,
    handover_text: str | None = None,
    roadmap_text: str | None = None,
    fail_closed: bool = False,
) -> CostAwarenessReport:
    """Build the active-slice spend-awareness report.

    When ``fail_closed`` is True (``overseer route`` path), malformed cost metadata
    raises ``RoutingPolicyError`` with exit ``32``. On informational surfaces
    (``status``, ``governance-sync``), malformed metadata degrades to a warning.
    """
    if not config.cost_awareness.enabled:
        return CostAwarenessReport(enabled=False)

    policy_rel = config.model_routing.policy
    try:
        policy_path = confine_path(repo_root, policy_rel)
    except PathEscapeError:
        violation = "model_routing.policy path escapes repo root"
        if fail_closed:
            raise RoutingPolicyError(violation, exit_code=31, citation=policy_rel)
        return CostAwarenessReport(
            enabled=True,
            policy=policy_rel,
            invalid=True,
            violation=violation,
        )

    try:
        cost_bands = load_model_tier_cost_bands(kit_root, fail_closed=fail_closed)
    except RoutingPolicyError as exc:
        if fail_closed:
            raise
        return CostAwarenessReport(
            enabled=True,
            policy=policy_rel,
            invalid=True,
            violation=exc.message,
        )

    try:
        policy = load_routing_policy(policy_path, kit_root=kit_root)
    except RoutingPolicyError as exc:
        if fail_closed:
            raise
        return CostAwarenessReport(
            enabled=True,
            policy=policy_rel,
            invalid=exc.exit_code != 31,
            violation=exc.message,
            exit_code=exc.exit_code,
        )

    gate_scan = scan_governance_gates(
        config,
        repo_root,
        handover_text=handover_text,
        roadmap_text=roadmap_text,
    )
    label_ids = load_label_ids(kit_root)
    roadmap = roadmap_text
    if roadmap is None:
        roadmap_path = repo_root / config.repo.root_relative_docs / config.docs.roadmap
        if roadmap_path.is_file():
            roadmap = roadmap_path.read_text(encoding="utf-8")

    slices: list[CostSlice] = []
    for phase_id in gate_scan.active_phases:
        model_label = model_label_for_phase(roadmap, phase_id)
        phase_tier = (
            normalize_phase_tier(model_label, label_ids=label_ids) if model_label else None
        )
        gate = gate_for_phase(gate_scan.pending, phase_id)
        query = RouteSelector(position=None, phase_tier=phase_tier, gate=gate)
        decision = resolve_route(policy, query)
        cost_class, paid = derive_cost_view(decision.model_tier, cost_bands)
        slices.append(
            CostSlice(
                phase_id=phase_id,
                phase_tier=phase_tier,
                gate=gate,
                route_id=decision.route_id,
                model_tier=decision.model_tier,
                cost_class=cost_class,
                paid_step_before_spend=paid,
            )
        )

    return CostAwarenessReport(enabled=True, policy=policy_rel, slices=tuple(slices))


def cost_awareness_payload(report: CostAwarenessReport) -> dict:
    """JSON payload for ``overseer status --json``."""
    if not report.enabled:
        return {"enabled": False}
    if report.invalid:
        return {
            "enabled": True,
            "policy": report.policy,
            "invalid": True,
            "violation": report.violation,
        }
    return {
        "enabled": True,
        "policy": report.policy,
        "slices": [
            {
                "phase_id": slice_.phase_id,
                "phase_tier": slice_.phase_tier,
                "gate": slice_.gate,
                "route_id": slice_.route_id,
                "model_tier": slice_.model_tier,
                "cost_class": slice_.cost_class,
                "paid_step_before_spend": slice_.paid_step_before_spend,
            }
            for slice_ in report.slices
        ],
    }

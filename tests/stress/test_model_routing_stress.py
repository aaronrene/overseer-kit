"""Stress tests for Track P / P-route (§PR.8)."""

from __future__ import annotations

import time

import yaml

from cli.kit_root import kit_root
from tools.model_routing.policy import load_routing_policy_text, parse_routing_policy
from tools.model_routing.resolve import resolve_route
from tools.model_routing.types import RouteSelector

BOUND_MS = 500


def _large_policy_yaml(route_count: int = 250) -> str:
    lines = [
        "version: 1",
        "defaults:",
        "  model_tier: standard",
        "  fallback: [standard, human]",
        "routes:",
    ]
    for index in range(route_count):
        lines.extend(
            [
                f"  - id: route-{index}",
                f"    when: {{ position: seat-{index % 17}, gate: default }}",
                "    model_tier: fast",
                "    fallback: [fast, standard, human]",
            ]
        )
    lines.extend(
        [
            "  - id: terminal-match",
            "    when: { position: target-seat }",
            "    model_tier: deep-reasoning",
            "    fallback: [deep-reasoning, human]",
        ]
    )
    return "\n".join(lines) + "\n"


def test_large_policy_resolves_within_bound() -> None:
    text = _large_policy_yaml()
    policy = parse_routing_policy(
        yaml.safe_load(text),
        kit_root=kit_root(),
        citation="large.yaml",
    )
    query = RouteSelector(position="target-seat")
    start = time.perf_counter()
    decision = resolve_route(policy, query)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert decision.route_id == "terminal-match"
    assert elapsed_ms < BOUND_MS


def test_large_policy_validate_within_bound() -> None:
    text = _large_policy_yaml()
    start = time.perf_counter()
    policy = load_routing_policy_text(text, kit_root=kit_root(), citation="large.yaml")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert policy.routes[-1].id == "terminal-match"
    assert elapsed_ms < BOUND_MS


def test_match_result_order_independent_under_fixed_policy() -> None:
    text = _large_policy_yaml(route_count=40)
    policy = load_routing_policy_text(text, kit_root=kit_root(), citation="large.yaml")
    query = RouteSelector(position="seat-3", gate="default")
    first = resolve_route(policy, query)
    second = resolve_route(policy, query)
    assert first == second

"""Unit tests for Track P / P-route model routing (§PR.8)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from adapters.errors import ConfigError
from cli.kit_root import kit_root
from tests.fixtures.model_routing import minimal_valid_policy_yaml, write_routing_policy
from tools.model_routing.labels import (
    load_model_tier_ids,
    validate_model_tier_entry,
    validate_model_tiers_document,
)
from tools.model_routing.policy import RoutingPolicyError, load_routing_policy_text, parse_routing_policy
from tools.model_routing.resolve import resolve_route, selector_matches
from tools.model_routing.types import RouteSelector


def test_model_tiers_required_fields() -> None:
    with pytest.raises(ConfigError, match="display"):
        validate_model_tier_entry({"id": "fast"}, index=0, path="policy/model-labels.yaml")


def test_model_tiers_unique_kebab_ids() -> None:
    raw = {
        "model_tiers": [
            {"id": "fast", "display": "Fast", "meaning": "quick"},
            {"id": "fast", "display": "Fast2", "meaning": "dup"},
        ]
    }
    with pytest.raises(ConfigError, match="unique"):
        validate_model_tiers_document(raw, path="policy/model-labels.yaml")


def test_model_tiers_reject_vendor_slug_id() -> None:
    with pytest.raises(ConfigError, match="vendor slug"):
        validate_model_tier_entry(
            {"id": "gpt-fast", "display": "Bad", "meaning": "bad"},
            index=0,
            path="policy/model-labels.yaml",
        )


def test_kit_model_tiers_load() -> None:
    ids = load_model_tier_ids(kit_root())
    assert ids == frozenset({"deep-reasoning", "standard", "fast", "local-offline"})


def test_routing_policy_requires_defaults() -> None:
    text = "version: 1\nroutes: []\n"
    with pytest.raises(RoutingPolicyError, match="defaults"):
        load_routing_policy_text(text, kit_root=kit_root(), citation="policy.yaml")


def test_routing_policy_rejects_unknown_when_key() -> None:
    text = """
version: 1
defaults:
  model_tier: standard
  fallback: [standard, human]
routes:
  - id: bad
    when: { extra: x }
    model_tier: standard
    fallback: [standard, human]
"""
    with pytest.raises(RoutingPolicyError, match="unknown"):
        load_routing_policy_text(text, kit_root=kit_root(), citation="policy.yaml")


def test_routing_policy_fallback_must_start_with_model_tier() -> None:
    text = """
version: 1
defaults:
  model_tier: standard
  fallback: [fast, human]
"""
    with pytest.raises(RoutingPolicyError, match="fallback\\[0\\]"):
        load_routing_policy_text(text, kit_root=kit_root(), citation="policy.yaml")


def test_routing_policy_fallback_must_end_with_human() -> None:
    text = """
version: 1
defaults:
  model_tier: standard
  fallback: [standard, fast]
"""
    with pytest.raises(RoutingPolicyError, match="terminate"):
        load_routing_policy_text(text, kit_root=kit_root(), citation="policy.yaml")


def test_routing_policy_rejects_unknown_model_tier() -> None:
    text = """
version: 1
defaults:
  model_tier: unknown-tier
  fallback: [unknown-tier, human]
"""
    with pytest.raises(RoutingPolicyError, match="not in model_tiers"):
        load_routing_policy_text(text, kit_root=kit_root(), citation="policy.yaml")


def test_routing_policy_duplicate_route_id() -> None:
    text = """
version: 1
defaults:
  model_tier: standard
  fallback: [standard, human]
routes:
  - id: dup
    when: {}
    model_tier: standard
    fallback: [standard, human]
  - id: dup
    when: {}
    model_tier: fast
    fallback: [fast, human]
"""
    with pytest.raises(RoutingPolicyError, match="duplicate"):
        load_routing_policy_text(text, kit_root=kit_root(), citation="policy.yaml")


def test_selector_wildcard_and_first_match() -> None:
    policy = parse_routing_policy(
        yaml.safe_load(minimal_valid_policy_yaml()),
        kit_root=kit_root(),
        citation="policy/model-routing.yaml",
    )
    assert not selector_matches(RouteSelector(position="overseer"), RouteSelector())
    assert selector_matches(
        RouteSelector(position="overseer"),
        RouteSelector(position="overseer"),
    )
    decision = resolve_route(policy, RouteSelector(position="overseer"))
    assert decision.route_id == "overseer-ruling"
    assert decision.model_tier == "deep-reasoning"


def test_defaults_fallthrough() -> None:
    policy = parse_routing_policy(
        yaml.safe_load(minimal_valid_policy_yaml()),
        kit_root=kit_root(),
        citation="policy/model-routing.yaml",
    )
    decision = resolve_route(policy, RouteSelector(position="unknown-seat"))
    assert decision.route_id == "defaults"
    assert decision.model_tier == "standard"
    assert decision.fallback == ("standard", "human")


def test_resolution_is_pure_no_io(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    policy = parse_routing_policy(
        yaml.safe_load(minimal_valid_policy_yaml()),
        kit_root=kit_root(),
        citation="policy/model-routing.yaml",
    )
    query = RouteSelector(phase_tier="auto")

    def _boom(*_args, **_kwargs):
        raise AssertionError("resolution must not perform I/O")

    monkeypatch.setattr(Path, "read_text", _boom)
    first = resolve_route(policy, query)
    second = resolve_route(policy, query)
    assert first == second
    assert first.route_id == "auto-build"

"""``policy/model-routing.yaml`` load and validation (§PR.4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools.freeze_reviewer.labels import is_vendor_slug
from tools.model_routing.labels import HUMAN_TIER, RoutingPolicyError, allowed_model_tier_ids
from tools.model_routing.types import PolicyValidationResult, RouteEntry, RouteSelector, RoutingPolicy

ROUTING_POLICY_VERSION = 1
TOP_LEVEL_KEYS = frozenset({"version", "defaults", "routes"})
DEFAULTS_KEYS = frozenset({"model_tier", "fallback"})
ROUTE_KEYS = frozenset({"id", "when", "model_tier", "fallback"})
WHEN_KEYS = frozenset({"position", "phase_tier", "gate"})
KIT_GATE_VALUES = frozenset({"freeze_review", "build_verification", "default"})


def load_routing_policy_text(text: str, *, kit_root: Path, citation: str) -> RoutingPolicy:
    """Parse routing policy YAML from text."""
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise RoutingPolicyError(
            f"unparseable routing policy YAML: {exc}",
            citation=citation,
        ) from exc
    return parse_routing_policy(raw, kit_root=kit_root, citation=citation)


def load_routing_policy(path: Path, *, kit_root: Path) -> RoutingPolicy:
    """Read and parse a routing policy file; exit ``31`` when missing/unreadable."""
    citation = str(path)
    if not path.is_file():
        raise RoutingPolicyError(
            "routing policy file missing or unreadable",
            exit_code=31,
            citation=citation,
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RoutingPolicyError(
            f"routing policy file missing or unreadable: {exc}",
            exit_code=31,
            citation=citation,
        ) from exc
    return load_routing_policy_text(text, kit_root=kit_root, citation=citation)


def parse_routing_policy(raw: Any, *, kit_root: Path, citation: str) -> RoutingPolicy:
    """Parse a routing policy mapping; raise ``RoutingPolicyError`` on violation."""
    if not isinstance(raw, dict):
        raise RoutingPolicyError("routing policy root must be a mapping", citation=citation)

    extra = set(raw) - TOP_LEVEL_KEYS
    if extra:
        raise RoutingPolicyError(
            f"unknown top-level routing policy keys: {sorted(extra)}",
            citation=citation,
        )

    version = raw.get("version")
    if version != ROUTING_POLICY_VERSION:
        raise RoutingPolicyError(
            f"unsupported routing policy version {version!r} (supported: {ROUTING_POLICY_VERSION})",
            citation=citation,
        )

    if "defaults" not in raw:
        raise RoutingPolicyError("routing policy missing mandatory defaults", citation=citation)

    allowed_tiers = allowed_model_tier_ids(kit_root)
    defaults_model_tier, defaults_fallback = _parse_route_target(
        raw["defaults"],
        field_prefix="defaults",
        citation=citation,
        allowed_tiers=allowed_tiers,
    )

    routes_raw = raw.get("routes", [])
    if routes_raw is None:
        routes_raw = []
    if not isinstance(routes_raw, list):
        raise RoutingPolicyError("routes must be a list", citation=citation)

    routes: list[RouteEntry] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(routes_raw):
        prefix = f"routes[{index}]"
        if not isinstance(item, dict):
            raise RoutingPolicyError(f"{prefix} must be a mapping", citation=citation)
        route_extra = set(item) - ROUTE_KEYS
        if route_extra:
            raise RoutingPolicyError(
                f"unknown {prefix} keys: {sorted(route_extra)}",
                citation=citation,
            )
        route_id = item.get("id")
        if not isinstance(route_id, str) or not route_id.strip():
            raise RoutingPolicyError(f"{prefix}.id must be a non-empty string", citation=citation)
        if route_id in seen_ids:
            raise RoutingPolicyError(f"duplicate route.id {route_id!r}", citation=citation)
        _reject_vendor_slug(route_id, f"{prefix}.id", citation)
        seen_ids.add(route_id)

        when = _parse_when(item.get("when"), prefix=prefix, citation=citation)
        model_tier, fallback = _parse_route_target(
            item,
            field_prefix=prefix,
            citation=citation,
            allowed_tiers=allowed_tiers,
        )
        routes.append(
            RouteEntry(
                id=route_id,
                when=when,
                model_tier=model_tier,
                fallback=fallback,
            )
        )

    _scan_strings_for_vendor_slugs(raw, citation=citation)
    return RoutingPolicy(
        version=ROUTING_POLICY_VERSION,
        defaults_model_tier=defaults_model_tier,
        defaults_fallback=defaults_fallback,
        routes=tuple(routes),
    )


def validate_routing_policy(path: Path, *, kit_root: Path) -> PolicyValidationResult:
    """Validate routing policy; return first violation with citation."""
    try:
        load_routing_policy(path, kit_root=kit_root)
    except RoutingPolicyError as exc:
        return PolicyValidationResult(valid=False, violation=_format_violation(exc))
    return PolicyValidationResult(valid=True)


def _format_violation(exc: RoutingPolicyError) -> str:
    if exc.citation:
        return f"{exc.citation}: {exc.message}"
    return exc.message


def _parse_when(raw_when: Any, *, prefix: str, citation: str) -> RouteSelector:
    if raw_when is None:
        return RouteSelector()
    if not isinstance(raw_when, dict):
        raise RoutingPolicyError(f"{prefix}.when must be a mapping", citation=citation)
    when_extra = set(raw_when) - WHEN_KEYS
    if when_extra:
        raise RoutingPolicyError(
            f"unknown {prefix}.when keys: {sorted(when_extra)}",
            citation=citation,
        )
    position = _optional_selector_value(raw_when, "position", prefix=prefix, citation=citation)
    phase_tier = _optional_selector_value(raw_when, "phase_tier", prefix=prefix, citation=citation)
    gate = _optional_selector_value(raw_when, "gate", prefix=prefix, citation=citation)
    if gate is not None and gate not in KIT_GATE_VALUES:
        raise RoutingPolicyError(
            f"{prefix}.when.gate must be freeze_review|build_verification|default",
            citation=citation,
        )
    return RouteSelector(position=position, phase_tier=phase_tier, gate=gate)


def _optional_selector_value(
    mapping: dict[str, Any],
    field: str,
    *,
    prefix: str,
    citation: str,
) -> str | None:
    if field not in mapping:
        return None
    value = mapping[field]
    if not isinstance(value, str) or not value.strip():
        raise RoutingPolicyError(f"{prefix}.when.{field} must be a non-empty string", citation=citation)
    return value


def _parse_route_target(
    mapping: dict[str, Any],
    *,
    field_prefix: str,
    citation: str,
    allowed_tiers: frozenset[str],
) -> tuple[str, tuple[str, ...]]:
    if field_prefix == "defaults":
        keys = DEFAULTS_KEYS
        extra = set(mapping) - DEFAULTS_KEYS
        if extra:
            raise RoutingPolicyError(
                f"unknown defaults keys: {sorted(extra)}",
                citation=citation,
            )
    else:
        keys = frozenset({"model_tier", "fallback"})

    if "model_tier" not in mapping:
        raise RoutingPolicyError(f"{field_prefix}.model_tier is required", citation=citation)
    model_tier = mapping["model_tier"]
    if not isinstance(model_tier, str) or not model_tier.strip():
        raise RoutingPolicyError(f"{field_prefix}.model_tier must be a non-empty string", citation=citation)
    if model_tier not in allowed_tiers:
        raise RoutingPolicyError(
            f"{field_prefix}.model_tier {model_tier!r} is not in model_tiers",
            citation=citation,
        )
    _reject_vendor_slug(model_tier, f"{field_prefix}.model_tier", citation)

    fallback_raw = mapping.get("fallback")
    if not isinstance(fallback_raw, list) or not fallback_raw:
        raise RoutingPolicyError(f"{field_prefix}.fallback must be a non-empty list", citation=citation)
    fallback: list[str] = []
    for index, item in enumerate(fallback_raw):
        if not isinstance(item, str) or not item.strip():
            raise RoutingPolicyError(
                f"{field_prefix}.fallback[{index}] must be a non-empty string",
                citation=citation,
            )
        if item not in allowed_tiers:
            raise RoutingPolicyError(
                f"{field_prefix}.fallback[{index}] {item!r} is not in model_tiers",
                citation=citation,
            )
        _reject_vendor_slug(item, f"{field_prefix}.fallback[{index}]", citation)
        fallback.append(item)

    if fallback[0] != model_tier:
        raise RoutingPolicyError(
            f"{field_prefix}.fallback[0] must equal {field_prefix}.model_tier",
            citation=citation,
        )
    if fallback[-1] != HUMAN_TIER:
        raise RoutingPolicyError(
            f"{field_prefix}.fallback must terminate in {HUMAN_TIER!r}",
            citation=citation,
        )
    return model_tier, tuple(fallback)


def _reject_vendor_slug(value: str, field: str, citation: str) -> None:
    if is_vendor_slug(value):
        raise RoutingPolicyError(f"{field} must not contain vendor slugs", citation=citation)


def _scan_strings_for_vendor_slugs(node: Any, *, citation: str, path: str = "") -> None:
    """Reject vendor slugs embedded in any string value (including comments rendered as values)."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            if isinstance(key, str):
                _reject_vendor_slug(key, child, citation)
            _scan_strings_for_vendor_slugs(value, citation=citation, path=child)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _scan_strings_for_vendor_slugs(value, citation=citation, path=f"{path}[{index}]")
    elif isinstance(node, str):
        if is_vendor_slug(node):
            raise RoutingPolicyError(f"{path or 'policy'} must not contain vendor slugs", citation=citation)

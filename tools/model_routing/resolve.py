"""Deterministic routing resolution (§PR.4)."""

from __future__ import annotations

from tools.model_routing.types import RouteDecision, RouteEntry, RouteSelector, RoutingPolicy


def selector_matches(when: RouteSelector, query: RouteSelector) -> bool:
    """Return True when every present ``when`` key equals the query value.

    Omitted ``when`` keys are wildcards. Omitted query keys do not satisfy a
    present ``when`` key — the query must explicitly provide each dimension a
    rule constrains.
    """
    for key in ("position", "phase_tier", "gate"):
        when_val = getattr(when, key)
        if when_val is None:
            continue
        query_val = getattr(query, key)
        if query_val is None or query_val != when_val:
            return False
    return True


def resolve_route(policy: RoutingPolicy, query: RouteSelector) -> RouteDecision:
    """Resolve ``query`` against ``policy`` using first-match-wins + mandatory defaults."""
    for route in policy.routes:
        if selector_matches(route.when, query):
            return RouteDecision(
                route_id=route.id,
                model_tier=route.model_tier,
                fallback=route.fallback,
            )
    return RouteDecision(
        route_id="defaults",
        model_tier=policy.defaults_model_tier,
        fallback=policy.defaults_fallback,
    )


def find_matching_route(policy: RoutingPolicy, query: RouteSelector) -> RouteEntry | None:
    """Return the first matching route entry, if any."""
    for route in policy.routes:
        if selector_matches(route.when, query):
            return route
    return None

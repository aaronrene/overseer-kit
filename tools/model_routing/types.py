"""Types for declarative model-routing (§PR.4)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteSelector:
    """Query or ``when`` selector triple; ``None`` means wildcard."""

    position: str | None = None
    phase_tier: str | None = None
    gate: str | None = None


@dataclass(frozen=True)
class RouteEntry:
    """One ordered routing rule."""

    id: str
    when: RouteSelector
    model_tier: str
    fallback: tuple[str, ...]


@dataclass(frozen=True)
class RoutingPolicy:
    """Parsed routing policy (version 1)."""

    version: int
    defaults_model_tier: str
    defaults_fallback: tuple[str, ...]
    routes: tuple[RouteEntry, ...]


@dataclass(frozen=True)
class RouteDecision:
    """Resolved routing decision returned by ``overseer route``."""

    route_id: str
    model_tier: str
    fallback: tuple[str, ...]


@dataclass(frozen=True)
class PolicyValidationResult:
    """Outcome of ``--validate`` or status policy-validity check."""

    valid: bool
    violation: str | None = None

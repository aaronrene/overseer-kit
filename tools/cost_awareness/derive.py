"""Deterministic ``paid_step_before_spend`` derivation (§PC.4)."""

from __future__ import annotations

from tools.model_routing.labels import HUMAN_TIER

COST_CLASS_ORDER = {"free": 0, "low": 1, "moderate": 2, "high": 3}


def derive_cost_view(
    model_tier: str,
    cost_bands: dict[str, str | None],
) -> tuple[str, bool]:
    """Return ``(cost_class, paid_step_before_spend)`` for a resolved tier.

    Pure function — no I/O. ``cost_bands`` maps tier id to declared band or
    ``None`` when the tier entry omits ``cost_class``.
    """
    if model_tier == HUMAN_TIER:
        return "free", False

    band = cost_bands.get(model_tier)
    if band is None:
        return "unknown", True
    if band == "free":
        return "free", False
    return band, True

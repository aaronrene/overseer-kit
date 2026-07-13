"""Format spend-awareness lines for CLI surfaces (§PC.7)."""

from __future__ import annotations

from tools.cost_awareness.surface import CostAwarenessReport, CostSlice


def format_cost_awareness_lines(report: CostAwarenessReport) -> tuple[str, ...]:
    """Human-readable spend-awareness lines for status and governance-sync."""
    if not report.enabled:
        return ()
    if report.invalid:
        return (f"cost_awareness: invalid — {report.violation}",)
    if not report.slices:
        return ("cost_awareness: no paid step in active slice",)
    if not any(slice_.paid_step_before_spend for slice_ in report.slices):
        return ("cost_awareness: no paid step in active slice",)
    return tuple(_format_slice(slice_) for slice_ in report.slices if slice_.paid_step_before_spend)


def _format_slice(slice_: CostSlice) -> str:
    tier = slice_.model_tier
    band = slice_.cost_class
    tier_label = f"{tier} ({band})" if band != "unknown" else tier
    tier_hint = f"[{slice_.phase_tier}]" if slice_.phase_tier else "[*]"
    paid = "paid step before spend" if slice_.paid_step_before_spend else "no metered spend"
    return f"cost_awareness: {slice_.phase_id} {tier_hint} → {tier_label} — {paid}"

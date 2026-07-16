"""Cost-awareness surface (Track P / P-cost §PC.4–§PC.7)."""

from tools.cost_awareness.derive import derive_cost_view
from tools.cost_awareness.format import format_cost_awareness_lines
from tools.cost_awareness.surface import build_cost_awareness_report

__all__ = [
    "build_cost_awareness_report",
    "derive_cost_view",
    "format_cost_awareness_lines",
]

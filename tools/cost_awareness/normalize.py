"""Phase Model-label and pending-gate normalization for active-slice routing (§PC.7)."""

from __future__ import annotations

import re

from tools.governance_gates.types import PendingGate

ROADMAP_ROW_RE = re.compile(
    r"^\|\s*\*\*(?P<phase>[^|*]+)\*\*\s*\|\s*(?P<model>[^|]+)\|\s*\*\*(?P<status>[^|*]+)\*\*\s*\|\s*(?P<deliverable>[^|]+)",
    re.MULTILINE,
)


def normalize_phase_tier(model_label: str, *, label_ids: frozenset[str]) -> str | None:
    """Map a roadmap ``Model:`` label to a ``labels[]`` id, or ``None`` (wildcard)."""
    cleaned = model_label.strip()
    if not cleaned:
        return None
    lowered = cleaned.lower()
    if lowered in label_ids:
        return lowered
    display_map = {
        "thinking": "thinking",
        "auto": "auto",
    }
    return display_map.get(lowered)


def gate_for_phase(pending: tuple[PendingGate, ...], phase_id: str) -> str | None:
    """Map pending governance gates for a phase to a routing ``gate`` selector."""
    phase_gates = [gate for gate in pending if gate.phase_id == phase_id]
    if any(gate.gate_id == "freeze_review" for gate in phase_gates):
        return "freeze_review"
    if any(gate.gate_id == "build_verification" for gate in phase_gates):
        return "build_verification"
    return None


def model_label_for_phase(roadmap: str | None, phase_id: str) -> str | None:
    """Read the roadmap model column for ``phase_id``."""
    if roadmap is None:
        return None
    normalized = _normalize_phase_id(phase_id)
    for match in ROADMAP_ROW_RE.finditer(roadmap):
        if _normalize_phase_id(match.group("phase")) == normalized:
            return match.group("model").strip()
    return None


def _normalize_phase_id(text: str) -> str:
    cleaned = text.strip()
    return re.sub(r"\s+", " ", cleaned)

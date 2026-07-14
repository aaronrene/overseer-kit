"""Document-derived gate parsers (§HGD.7.1).

Never invents ``DONE`` on garbage input.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

STATUS_TOKENS = frozenset({"TODO", "WIP", "DONE", "BLOCKED"})

# Build-status table rows: | **Phase** | Auto | **DONE** | ...
_BUILD_STATUS_ROW = re.compile(
    r"^\|\s*\*?\*?([^|*]+?)\*?\*?\s*\|\s*([^|]+?)\s*\|\s*\*?\*?(TODO|WIP|DONE|BLOCKED)\*?\*?\s*\|",
    re.IGNORECASE | re.MULTILINE,
)

# Status: DONE under a phase heading
_INLINE_STATUS = re.compile(
    r"(?im)^\s*(?:\*\*)?Status(?:\*\*)?\s*:\s*\*?\*?(TODO|WIP|DONE|BLOCKED)\*?\*?",
)

_PENDING_GATES = re.compile(
    r"(?is)pending[-\s]?gates[^\n]*\n+(.*?)(?=\n## |\n# |\Z)",
)


@dataclass(frozen=True)
class DocumentDerivedGates:
    """Parsed document-derived gate view."""

    ok: bool
    error: str | None
    phases: list[dict[str, str]]
    pending_gates_excerpt: str | None


def parse_document_derived_gates(
    *,
    roadmap_text: str | None,
    handover_text: str | None,
) -> DocumentDerivedGates:
    """Build document-derived gates from ROADMAP and/or HANDOVER text.

    On total parse failure (no usable text or zero recognizable status tokens
    when text claims build status poorly) returns ``ok: false`` without fabricating DONE.
    """
    phases: list[dict[str, str]] = []
    seen: set[str] = set()

    if roadmap_text:
        for match in _BUILD_STATUS_ROW.finditer(roadmap_text):
            phase_id = match.group(1).strip()
            status = match.group(3).upper()
            if status not in STATUS_TOKENS:
                continue
            if not phase_id or phase_id.lower() in {"phase", "id", "---"}:
                continue
            # Skip markdown separator rows
            if set(phase_id) <= {"-"}:
                continue
            key = phase_id.lower()
            if key in seen:
                continue
            seen.add(key)
            phases.append({"id": phase_id, "status": status})

    pending_excerpt: str | None = None
    if handover_text:
        pending_match = _PENDING_GATES.search(handover_text)
        if pending_match:
            excerpt = pending_match.group(1).strip()
            if excerpt:
                pending_excerpt = excerpt[:500]

    if roadmap_text is None and handover_text is None:
        return DocumentDerivedGates(
            ok=False,
            error="parse_failed",
            phases=[],
            pending_gates_excerpt=None,
        )

    # Garbage-only input with no recognizable phases → ok false, never invent DONE.
    garbage_roadmap = bool(roadmap_text) and not phases and _looks_like_status_claim(roadmap_text)
    if garbage_roadmap and not pending_excerpt:
        return DocumentDerivedGates(
            ok=False,
            error="parse_failed",
            phases=[],
            pending_gates_excerpt=None,
        )

    return DocumentDerivedGates(
        ok=True,
        error=None,
        phases=phases,
        pending_gates_excerpt=pending_excerpt,
    )


def _looks_like_status_claim(text: str) -> bool:
    """Heuristic: text mentions Status/DONE tokens but rows failed to parse."""
    lowered = text.lower()
    return "status" in lowered or "done" in lowered or "| " in text


def never_invent_done_on_garbage(text: str) -> DocumentDerivedGates:
    """Unit-test helper: garbage input must not invent DONE."""
    return parse_document_derived_gates(roadmap_text=text, handover_text=None)

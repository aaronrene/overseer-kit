"""Format pending governance gates for CLI surfaces (§KH1.9)."""

from __future__ import annotations

from tools.governance_gates.types import GateScanResult, PendingGate


def format_pending_gate_lines(result: GateScanResult) -> tuple[str, ...]:
    """Human-readable lines for status and governance-sync footers."""
    if result.suppressed:
        return ("governance-gates: reminders suppressed (Tier 2)",)
    if not result.pending:
        return ("governance-gates: none pending in active slice",)
    lines = ["Pending governance gates:"]
    for gate in result.pending:
        lines.append(_format_gate(gate))
    lines.append("Reminders only — acknowledge or invoke; silence is not pass.")
    return tuple(lines)


def pending_gates_payload(result: GateScanResult) -> dict:
    """JSON-serializable pending gates for ``overseer status --json``."""
    return {
        "enabled": result.enabled,
        "suppressed": result.suppressed,
        "active_phases": list(result.active_phases),
        "pending": [
            {
                "gate_id": gate.gate_id,
                "phase_id": gate.phase_id,
                "artifact": gate.artifact,
                "message": gate.message,
                "invoke": gate.invoke,
            }
            for gate in result.pending
        ],
    }


def _format_gate(gate: PendingGate) -> str:
    artifact = f" ({gate.artifact})" if gate.artifact else ""
    return f"- {gate.gate_id}: {gate.phase_id}{artifact} — {gate.message}; invoke: {gate.invoke}"

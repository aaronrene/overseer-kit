"""Governance gate reminders (§KH1.9) — read-only scan; never treat silence as pass."""

from tools.governance_gates.checklist import governance_gates_checklist_lines
from tools.governance_gates.scan import GateScanResult, PendingGate, scan_governance_gates

__all__ = [
    "GateScanResult",
    "PendingGate",
    "governance_gates_checklist_lines",
    "scan_governance_gates",
]

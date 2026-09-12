"""Governance gates reminder package (§KH1.9)."""

from __future__ import annotations

__all__ = ["GateScanResult", "PendingGate", "scan_governance_gates"]


def __getattr__(name: str):
    if name == "scan_governance_gates":
        from tools.governance_gates.scan import scan_governance_gates

        return scan_governance_gates
    if name in {"GateScanResult", "PendingGate"}:
        from tools.governance_gates import types as _types

        return getattr(_types, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

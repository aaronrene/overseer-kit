"""Governance Hygiene Agent (Phase 9A-5)."""

from __future__ import annotations

__all__ = [
    "DriftReport",
    "GovernanceSyncResult",
    "VerifiedReads",
    "detect_drift",
    "run_governance_sync",
]


def __getattr__(name: str):
    if name == "detect_drift":
        from tools.governance_hygiene.drift import detect_drift

        return detect_drift
    if name == "run_governance_sync":
        from tools.governance_hygiene.engine import run_governance_sync

        return run_governance_sync
    if name in {"DriftReport", "GovernanceSyncResult", "VerifiedReads"}:
        from tools.governance_hygiene import types as _types

        return getattr(_types, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

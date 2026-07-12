"""Types for governance gate reminders (§KH1.9)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PendingGate:
    """One pending governance gate detected by read-only scan."""

    gate_id: str  # freeze_review | build_verification | handover_paste
    phase_id: str
    artifact: str | None
    message: str
    invoke: str


@dataclass(frozen=True)
class GateScanResult:
    """Outcome of scanning roadmap + handover for pending gates."""

    enabled: bool
    suppressed: bool
    pending: tuple[PendingGate, ...]
    active_phases: tuple[str, ...]

    @property
    def has_pending(self) -> bool:
        return bool(self.pending)

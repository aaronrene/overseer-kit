"""Adversarial-freeze honesty gate (§AFF)."""

from __future__ import annotations

from tools.adversarial_freeze.authorize import (
    AffAuthState,
    AdversarialAuthorization,
    adversarial_authorization_state,
    aff_hold_bypassed,
    aggregate_adversarial_authorization_states,
    author_loop_complete,
    frv_authorizing_freeze_paths,
)
from tools.adversarial_freeze.surface import (
    AdversarialFreezeGateReport,
    build_adversarial_freeze_gate,
    format_adversarial_freeze_gate_line,
    adversarial_freeze_gate_payload,
)

__all__ = [
    "AffAuthState",
    "AdversarialAuthorization",
    "AdversarialFreezeGateReport",
    "adversarial_authorization_state",
    "adversarial_freeze_gate_payload",
    "aff_hold_bypassed",
    "aggregate_adversarial_authorization_states",
    "author_loop_complete",
    "build_adversarial_freeze_gate",
    "format_adversarial_freeze_gate_line",
    "frv_authorizing_freeze_paths",
]

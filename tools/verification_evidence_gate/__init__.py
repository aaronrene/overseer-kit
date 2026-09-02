"""Active-slice verification evidence gate for status / governance-sync (§LT.5.2)."""

from tools.verification_evidence_gate.surface import (
    VerificationEvidenceGateReport,
    build_verification_evidence_gate,
    format_verification_evidence_gate_line,
    verification_evidence_gate_payload,
)

__all__ = [
    "VerificationEvidenceGateReport",
    "build_verification_evidence_gate",
    "format_verification_evidence_gate_line",
    "verification_evidence_gate_payload",
]

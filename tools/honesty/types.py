"""Shared types for the L2 honesty module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

HonestyErrorToken = Literal[
    "usage",
    "config",
    "refused",
    "missing_verdict",
    "missing_verification_evidence",
    "missing_deploy_health",
    "approval_integrity",
    "ledger_broken",
    "role_violation",
    "evidence_free",
    "io",
    None,
]

ENTRY_KINDS = frozenset(
    {
        "genesis",
        "task_assigned",
        "verdict",
        "dispute_opened",
        "overseer_ruling",
        "approval_recorded",
        "board_advance",
        "hook_check",
        "verification_evidence",
    }
)

VERIFICATION_ARTIFACT_TYPES = frozenset({"test_output", "deploy_health", "screenshot"})
BV_VERDICTS = frozenset({"pass", "findings", "blocked"})

ACTOR_ROLES = frozenset({"owner", "overseer", "producer", "verifier"})

HOOK_NAMES = frozenset({"board_done", "handoff", "register"})


class EntryValidationError(Exception):
    """Raised when an append body fails schema or role checks."""

    def __init__(self, exit_code: int, message: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass
class HonestyStatusJson:
    """Frozen honesty-status JSON schema payload (§K9.9)."""

    ok: bool
    exit_code: int
    command: str = "honesty-status"
    hook: str | None = None
    artifact: str | None = None
    artifact_sha256: str | None = None
    producer_session: str | None = None
    matched_verdict_hash: str | None = None
    error: HonestyErrorToken = None
    verification_evidence: dict[str, Any] | None = None
    deploy_health: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": self.ok,
            "exit_code": self.exit_code,
            "command": self.command,
            "hook": self.hook,
            "artifact": self.artifact,
            "artifact_sha256": self.artifact_sha256,
            "producer_session": self.producer_session,
            "matched_verdict_hash": self.matched_verdict_hash,
            "error": self.error,
        }
        if self.verification_evidence is not None:
            payload["verification_evidence"] = self.verification_evidence
        if self.deploy_health is not None:
            payload["deploy_health"] = self.deploy_health
        return payload


@dataclass
class HonestyStatusResult:
    """Outcome of ``run_honesty_status``."""

    exit_code: int
    json_payload: HonestyStatusJson
    stderr_extra: str = ""


@dataclass
class LedgerAppendOptions:
    """Input for ``append_entry``."""

    kind: str
    body: dict[str, Any] = field(default_factory=dict)
    from_stdin: bool = False
    file_path: str | None = None


@dataclass
class LedgerResult:
    """Generic ledger command outcome."""

    exit_code: int
    stdout_lines: list[str] = field(default_factory=list)
    stderr_extra: str = ""

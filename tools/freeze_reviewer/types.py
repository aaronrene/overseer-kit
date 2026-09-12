"""Shared types for the freeze reviewer engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["BLOCKER", "MAJOR", "MINOR"]
Category = Literal[
    "security",
    "irreversible",
    "real_money",
    "gates_tier3",
    "completeness",
    "consistency",
    "other",
]
Verdict = Literal["pass", "findings", "blocked"]
EscalationReason = Literal["mode_human", "provider_unreachable"]
DeclarationStatus = Literal["present", "absent"]
ArtifactKind = Literal[
    "markdown_fence",
    "yaml_whole",
    "operator_forced_md",
    "operator_forced_yaml",
]

# §FRV.3.2 / §FRV.5.1 — CLI-owned stamp keys (fourteen) plus legacy verdict.
CLI_OWNED_STAMP_KEYS = frozenset(
    {
        "gate",
        "reviewed_at",
        "mechanical_verdict",
        "produced_by",
        "provider_kind",
        "reviewer_mode",
        "reviewer_model",
        "reviewer_provider",
        "checklist_ids",
        "checklist_source",
        "findings_count",
        "override_applied",
        "kit_version",
        "artifact_digest",
        "verdict",  # legacy — dropped on write
    }
)

STAMP_KEY_ORDER = (
    "gate",
    "reviewed_at",
    "mechanical_verdict",
    "produced_by",
    "provider_kind",
    "reviewer_mode",
    "reviewer_model",
    "reviewer_provider",
    "checklist_ids",
    "checklist_source",
    "findings_count",
    "override_applied",
    "kit_version",
    "artifact_digest",
)


@dataclass(frozen=True)
class ChecklistItem:
    """One checklist entry (built-in §K5.5 or operator file)."""

    id: str
    title: str
    typical_severity: Severity


@dataclass
class Finding:
    """A cited freeze-review finding (§K5.6)."""

    id: str = ""
    check: str = ""
    severity: Severity = "MINOR"
    category: Category = "other"
    path: str = ""
    line: int = 1
    message: str = ""
    citation: str = ""

    def with_citation(self) -> Finding:
        """Ensure citation matches path:line."""
        self.citation = f"{self.path}:{self.line}"
        return self

    def is_valid_citation(self) -> bool:
        return bool(self.path) and self.line >= 1 and self.citation == f"{self.path}:{self.line}"


@dataclass(frozen=True)
class ReviewerSettings:
    """Effective reviewer configuration for one invocation."""

    mode: str
    model: str | None
    provider: str | None
    fallback: str | None


@dataclass
class ReviewStamp:
    """Mechanical review stamp written on pass (§K5.7 / §FRV.3–§FRV.4)."""

    reviewed_at: str
    mechanical_verdict: Verdict
    reviewer_mode: str
    reviewer_model: str | None
    reviewer_provider: str | None
    kit_version: str
    artifact_digest: str
    gate: str = "mechanical"
    produced_by: str = "checklist_engine"
    provider_kind: str = "rule_engine"
    checklist_ids: list[str] = field(default_factory=list)
    checklist_source: str = "builtin"
    findings_count: int = 0
    override_applied: bool = False

    def to_mapping(self) -> dict:
        """Emit exactly the fourteen §FRV.3.2 keys in frozen order; never verdict."""
        return {
            "gate": self.gate,
            "reviewed_at": self.reviewed_at,
            "mechanical_verdict": self.mechanical_verdict,
            "produced_by": self.produced_by,
            "provider_kind": self.provider_kind,
            "reviewer_mode": self.reviewer_mode,
            "reviewer_model": self.reviewer_model,
            "reviewer_provider": self.reviewer_provider,
            "checklist_ids": list(self.checklist_ids),
            "checklist_source": self.checklist_source,
            "findings_count": self.findings_count,
            "override_applied": self.override_applied,
            "kit_version": self.kit_version,
            "artifact_digest": self.artifact_digest,
        }


@dataclass
class ReviewResult:
    """Internal review outcome before CLI exit mapping."""

    verdict: Verdict = "pass"
    findings: list[Finding] = field(default_factory=list)
    escalation: str | None = None
    reason: EscalationReason | None = None
    provider_cause: str | None = None
    stamp: ReviewStamp | None = None
    stamp_written: bool = False
    declaration: DeclarationStatus = "absent"
    artifact_kind: ArtifactKind = "operator_forced_md"
    dry_run: bool = False
    no_stamp: bool = False
    config_error: str | None = None
    refused: bool = False
    refuse_cause: str | None = None
    io_error: bool = False
    checklist_ids: list[str] = field(default_factory=list)
    escalation_refused: bool = False
    escalation_refuse_cause: str | None = None
    operator_block: bool | None = None
    existing_stamp_verdict: str | None = None

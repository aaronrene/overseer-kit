"""Shared types for the L1 checkpoint orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

VerifyMode = Literal["step", "through", "all"]
ErrorToken = Literal[
    "usage",
    "config",
    "refused",
    "step_order",
    "verify_fail",
    "io",
    None,
]


@dataclass
class StepState:
    """One manifest step entry."""

    verified: bool = False
    verified_at: str | None = None
    artifact_sha256: str | None = None


@dataclass
class ManifestState:
    """Parsed active work-unit manifest."""

    schema_version: int
    template_id: str
    slug: str
    current_step: str
    steps: dict[str, StepState]
    meta: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""


@dataclass
class StepDef:
    """One policy step definition."""

    verify_script: str
    description: str | None = None


@dataclass
class PolicyState:
    """Parsed checkpoint policy."""

    version: int
    placeholder_tokens: list[str]
    steps: dict[str, StepDef]
    templates: dict[str, list[str]]
    overrides_default: dict[str, Any]
    overrides_by_template: dict[str, dict[str, Any]]
    source_path: str = ""


@dataclass
class VerifyStepJson:
    """Frozen verify-step JSON schema payload."""

    ok: bool
    exit_code: int
    command: str = "verify-step"
    mode: VerifyMode | None = None
    dry_run: bool = False
    manifest: str | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    error: ErrorToken = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "exit_code": self.exit_code,
            "command": self.command,
            "mode": self.mode,
            "dry_run": self.dry_run,
            "manifest": self.manifest,
            "steps": self.steps,
            "error": self.error,
        }


@dataclass
class VerifyStepResult:
    """Outcome of ``run_verify_step``."""

    exit_code: int
    json_payload: VerifyStepJson
    stderr_extra: str = ""

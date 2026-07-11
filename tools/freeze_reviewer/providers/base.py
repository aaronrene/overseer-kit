"""Review provider interface and implementations (§K5.8)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Protocol

from tools.freeze_reviewer.checklist import BUILTIN_CHECKLIST
from tools.freeze_reviewer.types import ChecklistItem, Finding, ReviewerSettings

ABSOLUTE_PATH_RE = re.compile(r"(?:^|[\s`'\"])(/[A-Za-z0-9._-]+){2,}")
SECRET_RE = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+")
TIER_MATRIX_RE = re.compile(r"seven[- ]tier|7[- ]tier", re.IGNORECASE)
GROUND_TRUTH_RE = re.compile(r"frozen:\s*true|ground truth|ground-truth", re.IGNORECASE)


class ReviewProvider(Protocol):
    """Provider interface for freeze review."""

    def reachable(self) -> tuple[bool, str | None]:
        """Return reachability and optional non-secret cause."""

    def review(
        self,
        *,
        artifact_text: str,
        artifact_path: str,
        checklist: list[ChecklistItem],
        reviewer: ReviewerSettings,
    ) -> list[Finding]:
        """Return pre-validation findings."""


@dataclass
class ChecklistEngine:
    """Rule-based checklist evaluation shared by local and api providers.

    Heuristic detectors emit findings only for concrete risk *surfaces* (missing
    ground-truth/matrix evidence; absolute paths; secret-assignment patterns;
    missing citation discipline). C5–C7 (irreversibility / real money / Tier-3
    linkage) require judgment of whether the artifact *introduces* those risks —
    normative discussion of the words is not a finding. Nuanced C5–C7 verdicts
    come from scripted/model providers; this engine does not keyword-match
    escalation vocabulary (§K5.5 / SPEC §6.3).
    """

    def evaluate(
        self,
        *,
        artifact_text: str,
        artifact_path: str,
        checklist: list[ChecklistItem],
    ) -> list[Finding]:
        findings: list[Finding] = []
        lines = artifact_text.splitlines()
        check_ids = {item.id for item in checklist}

        if "C1" in check_ids and not GROUND_TRUTH_RE.search(artifact_text):
            findings.append(
                Finding(
                    check="C1",
                    severity="MAJOR",
                    category="completeness",
                    path=artifact_path,
                    line=1,
                    message="Missing ground-truth edge declaration.",
                ).with_citation()
            )

        if "C2" in check_ids and not TIER_MATRIX_RE.search(artifact_text):
            findings.append(
                Finding(
                    check="C2",
                    severity="BLOCKER",
                    category="completeness",
                    path=artifact_path,
                    line=1,
                    message="Missing seven-tier test matrix section.",
                ).with_citation()
            )

        if "C4" in check_ids:
            for line_no, line in enumerate(lines, start=1):
                if ABSOLUTE_PATH_RE.search(line):
                    findings.append(
                        Finding(
                            check="C4",
                            severity="BLOCKER",
                            category="security",
                            path=artifact_path,
                            line=line_no,
                            message="Absolute machine path appears in artifact text.",
                        ).with_citation()
                    )
                    break
                if SECRET_RE.search(line):
                    findings.append(
                        Finding(
                            check="C4",
                            severity="BLOCKER",
                            category="security",
                            path=artifact_path,
                            line=line_no,
                            message="Secret-like token pattern appears in artifact text.",
                        ).with_citation()
                    )
                    break

        if "C8" in check_ids and "file+line" not in artifact_text.lower():
            findings.append(
                Finding(
                    check="C8",
                    severity="MINOR",
                    category="consistency",
                    path=artifact_path,
                    line=1,
                    message="Citation readiness discipline not evidenced in artifact.",
                ).with_citation()
            )

        return findings


@dataclass
class LocalReviewProvider:
    """Offline-capable local provider (§K5.8)."""

    engine: ChecklistEngine = field(default_factory=ChecklistEngine)
    force_unreachable: bool = False
    unreachable_cause: str | None = None
    scripted_findings: list[Finding] | None = None
    review_calls: int = 0
    reachable_calls: int = 0

    def reachable(self) -> tuple[bool, str | None]:
        self.reachable_calls += 1
        if self.force_unreachable:
            return False, self.unreachable_cause or "local runner unavailable"
        return True, None

    def review(
        self,
        *,
        artifact_text: str,
        artifact_path: str,
        checklist: list[ChecklistItem],
        reviewer: ReviewerSettings,
    ) -> list[Finding]:
        self.review_calls += 1
        if self.scripted_findings is not None:
            return list(self.scripted_findings)
        return self.engine.evaluate(
            artifact_text=artifact_text,
            artifact_path=artifact_path,
            checklist=checklist,
        )


@dataclass
class ApiReviewProvider:
    """Remote API provider with shared engine surface (§K5.8)."""

    engine: ChecklistEngine = field(default_factory=ChecklistEngine)
    env_var: str = "OVERSEER_REVIEW_API_KEY"
    scripted_findings: list[Finding] | None = None
    review_calls: int = 0
    reachable_calls: int = 0

    def reachable(self) -> tuple[bool, str | None]:
        self.reachable_calls += 1
        if os.environ.get(self.env_var):
            return True, None
        return False, "missing API credentials"

    def review(
        self,
        *,
        artifact_text: str,
        artifact_path: str,
        checklist: list[ChecklistItem],
        reviewer: ReviewerSettings,
    ) -> list[Finding]:
        self.review_calls += 1
        if self.scripted_findings is not None:
            return list(self.scripted_findings)
        return self.engine.evaluate(
            artifact_text=artifact_text,
            artifact_path=artifact_path,
            checklist=checklist,
        )


def provider_for(settings: ReviewerSettings, provider: ReviewProvider | None = None) -> ReviewProvider:
    """Construct the effective provider unless a test double is injected."""
    if provider is not None:
        return provider
    if settings.provider == "api":
        return ApiReviewProvider()
    return LocalReviewProvider()

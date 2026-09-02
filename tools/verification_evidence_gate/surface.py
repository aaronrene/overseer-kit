"""Active-slice Mode B verification evidence surface (§LT.5.2)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from adapters.config import OverseerConfig
from cli.paths import confine_path
from tools.governance_gates.scan import (
    BUILD_VERIFICATION_PASS_RE,
    PHASE_DOC_RE,
    ROADMAP_ROW_RE,
    _is_auto_model,
    _normalize_phase_id,
    scan_governance_gates,
)
from tools.honesty.ledger import read_ledger_entries
from tools.honesty.validate import find_matching_verification_evidence

AUTO_B_STEP_RE = re.compile(r"\bb\b$", re.IGNORECASE)


@dataclass(frozen=True)
class VerificationEvidenceGateReport:
    """Result of the active-slice verification evidence probe."""

    skipped: bool
    ok: bool
    mode: str | None = None
    matched: bool | None = None
    phase_id: str | None = None
    message: str | None = None
    token: str | None = None


def build_verification_evidence_gate(
    config: OverseerConfig,
    repo_root: Path,
    *,
    handover_text: str | None = None,
    roadmap_text: str | None = None,
) -> VerificationEvidenceGateReport:
    """Run active-slice Mode B when honesty warn/require is enabled."""
    require = config.honesty.require_verification_evidence
    if not config.honesty.enabled or require not in {"warn", "require"}:
        return VerificationEvidenceGateReport(skipped=True, ok=True)

    docs_root = config.repo.root_relative_docs
    handover_path = repo_root / docs_root / config.docs.handover
    roadmap_path = repo_root / docs_root / config.docs.roadmap
    handover = handover_text if handover_text is not None else _read_text(handover_path)
    roadmap = roadmap_text if roadmap_text is not None else _read_text(roadmap_path)

    gate_scan = scan_governance_gates(
        config,
        repo_root,
        handover_text=handover,
        roadmap_text=roadmap,
    )
    if not gate_scan.active_phases:
        return VerificationEvidenceGateReport(skipped=True, ok=True)

    phase_id = _select_active_auto_phase(roadmap, gate_scan.active_phases)
    if phase_id is None:
        return VerificationEvidenceGateReport(skipped=True, ok=True)

    if not _should_run_mode_b(phase_id, handover, roadmap):
        return VerificationEvidenceGateReport(skipped=True, ok=True)

    frozen_spec = _frozen_spec_for_phase(roadmap, phase_id)
    matched = _ledger_match(config, repo_root, phase_id, frozen_spec)

    if matched:
        return VerificationEvidenceGateReport(
            skipped=False,
            ok=True,
            mode=require,
            matched=True,
            phase_id=phase_id,
        )

    if require == "require":
        return VerificationEvidenceGateReport(
            skipped=False,
            ok=False,
            mode=require,
            matched=False,
            phase_id=phase_id,
            message="missing verification_evidence ledger entry for active Auto slice",
            token="missing_verification_evidence",
        )

    return VerificationEvidenceGateReport(
        skipped=False,
        ok=True,
        mode="warn",
        matched=False,
        phase_id=phase_id,
        message="warning: no matching verification_evidence entry for active Auto slice",
    )


def verification_evidence_gate_payload(report: VerificationEvidenceGateReport) -> dict | None:
    if report.skipped:
        return None
    payload: dict = {
        "ok": report.ok,
        "mode": report.mode,
        "matched": report.matched,
    }
    if report.phase_id:
        payload["phase_id"] = report.phase_id
    if report.token:
        payload["token"] = report.token
    return payload


def format_verification_evidence_gate_line(report: VerificationEvidenceGateReport) -> str | None:
    if report.skipped or report.message is None:
        return None
    return f"verification_evidence_gate: {report.message}"


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _select_active_auto_phase(roadmap: str | None, active: tuple[str, ...]) -> str | None:
    if roadmap is None:
        return None
    for phase_id in active:
        row = _roadmap_row(roadmap, phase_id)
        if row is None:
            continue
        model = row.group("model")
        if _is_active_auto_model(model, phase_id):
            return phase_id
    return None


def _is_active_auto_model(model: str, phase_id: str) -> bool:
    if not _is_auto_model(model):
        return False
    lowered = model.lower()
    if "thinking" in lowered and "auto" in lowered:
        # Thinking → Auto split: only the Auto half ({step}b) is in scope.
        return bool(AUTO_B_STEP_RE.search(phase_id.replace(" ", "")))
    return True


def _roadmap_row(roadmap: str, phase_id: str):
    normalized = _normalize_phase_id(phase_id)
    tokens = [token for token in re.split(r"[\s/]+", normalized.lower()) if token]
    for match in ROADMAP_ROW_RE.finditer(roadmap):
        phase_label = _normalize_phase_id(match.group("phase"))
        if phase_label == normalized:
            return match
        phase_lower = phase_label.lower()
        if tokens and all(token in phase_lower for token in tokens):
            return match
    return None


def _roadmap_status(roadmap: str, phase_id: str) -> str | None:
    row = _roadmap_row(roadmap, phase_id)
    if row is None:
        return None
    return row.group("status").strip().upper()


def _claims_done_or_bv_pass(corpus: str, phase_id: str) -> bool:
    if _roadmap_status(corpus, phase_id) == "DONE":
        return True
    if not BUILD_VERIFICATION_PASS_RE.search(corpus):
        return False
    phase_tokens = [token for token in re.split(r"[\s/]+", phase_id.lower()) if token]
    if not phase_tokens:
        return False
    window = 400
    for match in BUILD_VERIFICATION_PASS_RE.finditer(corpus):
        start = max(0, match.start() - window)
        end = min(len(corpus), match.end() + window)
        snippet = corpus[start:end].lower()
        if any(token in snippet for token in phase_tokens):
            return True
    return False


def _should_run_mode_b(phase_id: str, handover: str | None, roadmap: str | None) -> bool:
    corpus = (handover or "") + "\n" + (roadmap or "")
    status = _roadmap_status(roadmap or "", phase_id)
    if status in {"TODO", "WIP"} and not _claims_done_or_bv_pass(corpus, phase_id):
        return False
    return _claims_done_or_bv_pass(corpus, phase_id)


def _frozen_spec_for_phase(roadmap: str | None, phase_id: str) -> str | None:
    if roadmap is None:
        return None
    row = _roadmap_row(roadmap, phase_id)
    if row is None:
        return None
    matches = PHASE_DOC_RE.findall(row.group("deliverable"))
    if len(matches) != 1:
        return None
    return matches[0]


def _ledger_match(
    config: OverseerConfig,
    repo_root: Path,
    phase_id: str,
    frozen_spec: str | None,
) -> bool:
    ledger_rel = config.honesty.ledger
    if ledger_rel is None or not ledger_rel.strip():
        return False
    try:
        ledger_path = confine_path(repo_root, ledger_rel)
    except Exception:
        return False
    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        return False
    try:
        entries = read_ledger_entries(ledger_path)
    except (ValueError, OSError):
        return False
    return find_matching_verification_evidence(
        entries,
        phase_id=phase_id,
        frozen_spec=frozen_spec,
    ) is not None

"""Read-only governance gate scan against roadmap + handover (§KH1.9)."""

from __future__ import annotations

import re
from pathlib import Path

from adapters.config import GovernanceGatesConfig, OverseerConfig
from tools.freeze_reviewer.artifact import extract_existing_stamp, parse_artifact
from tools.governance_gates.checklist import (
    BUILD_VERIFICATION_INVOKE,
    FREEZE_REVIEW_INVOKE,
)
from tools.governance_gates.types import GateScanResult, PendingGate

ROADMAP_ROW_RE = re.compile(
    r"^\|\s*\*\*(?P<phase>[^|*]+)\*\*\s*\|\s*(?P<model>[^|]+)\|\s*\*\*(?P<status>[^|*]+)\*\*\s*\|\s*(?P<deliverable>[^|]+)",
    re.MULTILINE,
)
PHASE_DOC_RE = re.compile(r"docs/PHASE-[A-Za-z0-9_.-]+\.md")
NEXT_ID_RE = re.compile(r"\|\s*\*\*ID\*\*\s*\|\s*\*\*([^*]+)\*\*", re.MULTILINE)
BUILD_VERIFICATION_PASS_RE = re.compile(
    r"build[- ]verification(?:[- ]review)?[^\n]{0,80}\bpass\b",
    re.IGNORECASE,
)
HANDOVER_PASTE_MARKER = "Governance gates"


def scan_governance_gates(
    config: OverseerConfig,
    repo_root: Path,
    *,
    handover_text: str | None = None,
    roadmap_text: str | None = None,
) -> GateScanResult:
    """Scan active roadmap slice for pending freeze review / build verification gates."""
    gates = config.governance_gates
    if not gates.remind:
        return GateScanResult(
            enabled=True,
            suppressed=True,
            pending=(),
            active_phases=(),
        )

    handover_path = repo_root / config.repo.root_relative_docs / config.docs.handover
    roadmap_path = repo_root / config.repo.root_relative_docs / config.docs.roadmap
    handover = handover_text if handover_text is not None else _read_text(handover_path)
    roadmap = roadmap_text if roadmap_text is not None else _read_text(roadmap_path)

    active = _active_phases(handover, roadmap)
    pending: list[PendingGate] = []

    if gates.freeze_review_required:
        pending.extend(_scan_freeze_review(repo_root, config, roadmap, active))

    if gates.build_verification_required:
        pending.extend(_scan_build_verification(handover, roadmap, active))

    if "handover-paste" in gates.surfaces and handover is not None:
        if HANDOVER_PASTE_MARKER not in handover:
            pending.append(
                PendingGate(
                    gate_id="handover_paste",
                    phase_id=_next_phase_id(handover) or "unknown",
                    artifact=config.docs.handover,
                    message="handover paste-ready prompt missing Governance gates checklist",
                    invoke="include §KH1.9 checklist in paste-ready prompt fence",
                )
            )

    return GateScanResult(
        enabled=True,
        suppressed=False,
        pending=tuple(pending),
        active_phases=active,
    )


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _active_phases(handover: str | None, roadmap: str | None) -> tuple[str, ...]:
    phases: set[str] = set()
    if handover:
        next_id = _next_phase_id(handover)
        if next_id:
            phases.add(_normalize_phase_id(next_id))
    if roadmap:
        for match in ROADMAP_ROW_RE.finditer(roadmap):
            status = match.group("status").strip().upper()
            if status in {"WIP", "TODO", "BLOCKED"}:
                phases.add(_normalize_phase_id(match.group("phase")))
    return tuple(sorted(phases))


def _next_phase_id(handover: str) -> str | None:
    match = NEXT_ID_RE.search(handover)
    if not match:
        return None
    return match.group(1).strip()


def _normalize_phase_id(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _scan_freeze_review(
    repo_root: Path,
    config: OverseerConfig,
    roadmap: str | None,
    active: tuple[str, ...],
) -> list[PendingGate]:
    pending: list[PendingGate] = []
    docs_root = repo_root / config.repo.root_relative_docs
    for phase_id in active:
        contract = _contract_path_for_phase(repo_root, docs_root, roadmap, phase_id)
        if contract is None or not contract.is_file():
            continue
        rel = contract.relative_to(repo_root).as_posix()
        try:
            parsed = parse_artifact(contract, rel_path=rel)
        except (ValueError, OSError):
            continue
        if parsed.declaration != "present":
            continue
        stamp = extract_existing_stamp(parsed)
        if stamp and stamp.get("verdict") == "pass":
            continue
        if _narrative_freeze_pass(contract.read_text(encoding="utf-8")):
            continue
        pending.append(
            PendingGate(
                gate_id="freeze_review",
                phase_id=phase_id,
                artifact=rel,
                message=f"frozen artifact lacks reviewed → pass ({rel})",
                invoke=FREEZE_REVIEW_INVOKE,
            )
        )
    return pending


def _scan_build_verification(
    handover: str | None,
    roadmap: str | None,
    active: tuple[str, ...],
) -> list[PendingGate]:
    if roadmap is None:
        return []
    pending: list[PendingGate] = []
    corpus = (handover or "") + "\n" + roadmap
    for match in ROADMAP_ROW_RE.finditer(roadmap):
        phase_label = _normalize_phase_id(match.group("phase"))
        if phase_label not in active:
            continue
        model = match.group("model")
        status = match.group("status").strip().upper()
        if not _is_auto_model(model):
            continue
        if status not in {"WIP", "DONE"}:
            continue
        if _build_verification_recorded(corpus, phase_label):
            continue
        pending.append(
            PendingGate(
                gate_id="build_verification",
                phase_id=phase_label,
                artifact=None,
                message=(
                    f"Auto phase {status} without recorded build-verification pass "
                    f"({phase_label})"
                ),
                invoke=BUILD_VERIFICATION_INVOKE,
            )
        )
    return pending


def _is_auto_model(model: str) -> bool:
    lowered = model.lower()
    if "auto" not in lowered:
        return False
    if lowered.strip() == "thinking":
        return False
    return True


def _build_verification_recorded(corpus: str, phase_id: str) -> bool:
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


def _contract_path_for_phase(
    repo_root: Path,
    docs_root: Path,
    roadmap: str | None,
    phase_id: str,
) -> Path | None:
    if roadmap:
        for row in ROADMAP_ROW_RE.finditer(roadmap):
            if _normalize_phase_id(row.group("phase")) != phase_id:
                continue
            deliverable = row.group("deliverable")
            doc_match = PHASE_DOC_RE.search(deliverable)
            if doc_match:
                candidate = (repo_root / doc_match.group(0)).resolve()
                if not str(candidate).startswith(str(repo_root.resolve())):
                    return None
                return candidate
    slug = re.sub(r"[^A-Za-z0-9]+", "-", phase_id).strip("-").upper()
    candidates = sorted(docs_root.glob(f"PHASE-{slug}*.md"))
    if candidates:
        return candidates[0]
    token = phase_id.split()[0].upper()
    candidates = sorted(docs_root.glob(f"PHASE-{token}*.md"))
    return candidates[0] if candidates else None


def _narrative_freeze_pass(text: str) -> bool:
    return bool(
        re.search(r"reviewed\s*→\s*`pass`", text, re.IGNORECASE)
        or re.search(r"Freeze status:.*\bpass\b", text, re.IGNORECASE)
        or re.search(r"→\s*`pass`.*Cleared", text, re.IGNORECASE)
    )

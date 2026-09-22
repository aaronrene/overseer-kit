"""Active-slice adversarial-freeze status / governance-sync surface (§AFF.9)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from adapters.config import OverseerConfig
from tools.adversarial_freeze.authorize import (
    adversarial_authorization_state,
    aff_hold_bypassed,
    aggregate_adversarial_authorization_states,
    frv_authorizing_freeze_paths,
)
from tools.governance_gates.scan import (
    ROADMAP_ROW_RE,
    _is_auto_model,
    _normalize_phase_id,
    scan_governance_gates,
)
from tools.governance_hygiene.parse import compact_step_id

# discover_freeze_candidates is imported lazily inside build_adversarial_freeze_gate
# to avoid a circular import:
#   next_regen → adversarial_freeze.authorize → package __init__ → surface → next_regen

AUTO_B_STEP_RE = re.compile(r"\bb\b$", re.IGNORECASE)

WARN_PENDING = (
    "warning: no authorizing adversarial_freeze entry for active Auto slice"
)
WARN_ABSENT = (
    "warning: adversarial_freeze unreadable (broken ledger or artifact) "
    "for active Auto slice"
)


@dataclass(frozen=True)
class AdversarialFreezeGateReport:
    """Result of the active-slice adversarial-freeze probe (§AFF.9)."""

    skipped: bool
    ok: bool
    mode: str | None = None
    state: str | None = None
    matched: bool | None = None
    message: str | None = None
    token: str | None = None


def build_adversarial_freeze_gate(
    config: OverseerConfig,
    repo_root: Path,
    *,
    handover_text: str | None = None,
    roadmap_text: str | None = None,
) -> AdversarialFreezeGateReport:
    """Run active-slice AFF probe when honesty suggest/require is enabled."""
    if aff_hold_bypassed(config):
        return AdversarialFreezeGateReport(skipped=True, ok=True)

    mode = config.honesty.adversarial_freeze
    if mode not in {"suggest", "require"}:
        return AdversarialFreezeGateReport(skipped=True, ok=True)

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
        return AdversarialFreezeGateReport(skipped=True, ok=True)

    phase_id = _select_active_auto_phase(roadmap, gate_scan.active_phases)
    if phase_id is None:
        return AdversarialFreezeGateReport(skipped=True, ok=True)

    row = _roadmap_row(roadmap or "", phase_id)
    if row is None:
        return AdversarialFreezeGateReport(skipped=True, ok=True)

    step_id = compact_step_id(row.group("phase"))
    from tools.governance_hygiene.next_regen import discover_freeze_candidates

    candidates = discover_freeze_candidates(
        repo_root, step_id, row.group("deliverable")
    )
    if not candidates:
        return AdversarialFreezeGateReport(skipped=True, ok=True)

    authorizing = frv_authorizing_freeze_paths(
        repo_root, candidates, phase_id=step_id, config=config
    )
    if not authorizing:
        return AdversarialFreezeGateReport(skipped=True, ok=True)

    states: list[str] = []
    for path in authorizing:
        auth = adversarial_authorization_state(repo_root, path, config=config)
        if auth.state == "off":
            continue
        states.append(auth.state)

    if not states:
        return AdversarialFreezeGateReport(skipped=True, ok=True)

    aggregated = aggregate_adversarial_authorization_states(states)
    matched = aggregated in {"pass", "skipped"}

    if matched:
        return AdversarialFreezeGateReport(
            skipped=False,
            ok=True,
            mode=mode,
            state=aggregated,
            matched=True,
        )

    if mode == "require":
        return AdversarialFreezeGateReport(
            skipped=False,
            ok=False,
            mode=mode,
            state=aggregated,
            matched=False,
            message="missing adversarial_freeze ledger entry for active Auto slice",
            token="missing_adversarial_freeze",
        )

    message = WARN_ABSENT if aggregated == "absent" else WARN_PENDING
    return AdversarialFreezeGateReport(
        skipped=False,
        ok=True,
        mode=mode,
        state=aggregated,
        matched=False,
        message=message,
    )


def adversarial_freeze_gate_payload(
    report: AdversarialFreezeGateReport,
) -> dict | None:
    if report.skipped:
        return None
    payload: dict = {
        "ok": report.ok,
        "mode": report.mode,
        "state": report.state,
        "matched": report.matched,
    }
    if report.token:
        payload["token"] = report.token
    return payload


def format_adversarial_freeze_gate_line(
    report: AdversarialFreezeGateReport,
) -> str | None:
    if report.skipped or report.message is None:
        return None
    return report.message


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

"""Stamp resolution and freeze Auto-authorization state (§FRV.3.4 / §FRV.6.4)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from adapters.config import OverseerConfig
from cli.paths import PathEscapeError, confine_path
from tools.freeze_reviewer.artifact import (
    artifact_digest,
    extract_existing_stamp,
    parse_artifact,
)
from tools.honesty.gate import honesty_module_disabled
from tools.honesty.ledger import verify_chain
from tools.honesty.ledger_io import read_ledger_entries
from tools.honesty.validate import find_matching_freeze_review

# §FRV.3.4 — kit-version property; flipping to False is a separate phase (not FRV-b).
# No config knob. Window: every kit version below 0.3.0.
ACCEPT_LEGACY_VERDICT_STAMP = True

AuthState = Literal[
    "substantive",
    "mechanical_only",
    "non_pass",
    "blocked_by_operator",
    "absent",
]

ResolvedKind = Literal["mechanical", "forged_substantive", "unreadable", "none"]


@dataclass(frozen=True)
class ResolvedStamp:
    """Result of §FRV.3.4 stamp mapping resolution."""

    kind: ResolvedKind
    verdict: str | None = None
    advisory: str | None = None


@dataclass(frozen=True)
class FreezeAuthorization:
    """Shared authorization state for next_regen + governance_gates (§FRV.6.4)."""

    state: AuthState
    advisory: str | None = None
    matched_entry_hash: str | None = None


def resolve_stamp_record(stamp_mapping: dict[str, Any] | None) -> ResolvedStamp:
    """Resolve a stamp mapping per §FRV.3.4 (six-branch order)."""
    if not isinstance(stamp_mapping, dict):
        return ResolvedStamp(kind="none")

    if "gate" in stamp_mapping:
        gate = stamp_mapping.get("gate")
        if gate == "mechanical":
            verdict = stamp_mapping.get("mechanical_verdict")
            verdict_s = str(verdict).strip() if verdict is not None else ""
            return ResolvedStamp(kind="mechanical", verdict=verdict_s or None)
        if gate == "substantive":
            return ResolvedStamp(
                kind="forged_substantive",
                advisory="forged_substantive_gate",
            )
        if not isinstance(gate, str):
            return ResolvedStamp(kind="unreadable", advisory="unreadable_gate")
        return ResolvedStamp(kind="unreadable", advisory="unreadable_gate")

    if "mechanical_verdict" in stamp_mapping:
        verdict = stamp_mapping.get("mechanical_verdict")
        verdict_s = str(verdict).strip() if verdict is not None else ""
        return ResolvedStamp(kind="mechanical", verdict=verdict_s or None)

    if "verdict" in stamp_mapping and ACCEPT_LEGACY_VERDICT_STAMP:
        verdict = stamp_mapping.get("verdict")
        verdict_s = str(verdict).strip() if verdict is not None else ""
        return ResolvedStamp(kind="mechanical", verdict=verdict_s or None)

    return ResolvedStamp(kind="none")


def _resolve_ledger_path_safe(config: OverseerConfig, repo_root: Path) -> Path | None:
    """Mirror honesty.ledger._resolve_ledger_path; failures → None (non-authorizing)."""
    try:
        honesty = getattr(config, "honesty", None)
        if honesty is None:
            return None
        ledger = getattr(honesty, "ledger", None)
        if ledger is None or not str(ledger).strip():
            return None
        return confine_path(repo_root, str(ledger))
    except (PathEscapeError, ValueError, TypeError, AttributeError, OSError):
        return None


def freeze_authorization_state(
    repo_root: Path,
    artifact_path: Path,
    *,
    phase_id: str,
    config: OverseerConfig,
) -> FreezeAuthorization:
    """Evaluate Auto-authorization state per §FRV.6.4 (fail-closed, never raise)."""
    try:
        return _freeze_authorization_state_impl(
            repo_root, artifact_path, phase_id=phase_id, config=config
        )
    except Exception:
        return FreezeAuthorization(state="absent")


def _freeze_authorization_state_impl(
    repo_root: Path,
    artifact_path: Path,
    *,
    phase_id: str,
    config: OverseerConfig,
) -> FreezeAuthorization:
    # 1. Parse artifact
    try:
        rel = artifact_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        try:
            rel = artifact_path.as_posix()
        except Exception:
            return FreezeAuthorization(state="absent")

    try:
        parsed = parse_artifact(artifact_path, rel_path=rel)
    except (ValueError, OSError, UnicodeError):
        return FreezeAuthorization(state="absent")

    # 2. auto_may_start (before ledger)
    freeze_mapping = parsed.freeze_mapping
    if isinstance(freeze_mapping, dict) and "auto_may_start" in freeze_mapping:
        auto_val = freeze_mapping.get("auto_may_start")
        if auto_val is True:
            pass  # no effect
        elif auto_val is False:
            return FreezeAuthorization(
                state="blocked_by_operator",
                advisory="operator_block",
            )
        else:
            return FreezeAuthorization(
                state="blocked_by_operator",
                advisory="operator_block_malformed",
            )

    # 3. Digest
    try:
        digest = artifact_digest(parsed)
    except Exception:
        return FreezeAuthorization(state="absent")

    frozen_spec = rel
    advisory: str | None = None

    # 4–6. Ledger match (only when honesty enabled)
    if not honesty_module_disabled(config):
        ledger_path = _resolve_ledger_path_safe(config, repo_root)
        if ledger_path is not None and ledger_path.is_file():
            try:
                entries = read_ledger_entries(ledger_path)
            except (ValueError, OSError):
                entries = None
            if entries is not None:
                chain_code = verify_chain(entries)
                if chain_code != 0:
                    advisory = "ledger_chain_broken"
                else:
                    match = find_matching_freeze_review(
                        entries,
                        phase_id=phase_id,
                        frozen_spec=frozen_spec,
                        artifact_digest=digest,
                    )
                    if match is not None:
                        return FreezeAuthorization(
                            state="substantive",
                            matched_entry_hash=str(match.get("entry_hash") or "") or None,
                        )

    # 7. Stamp resolve
    stamp = extract_existing_stamp(parsed)
    resolved = resolve_stamp_record(stamp)
    if resolved.kind == "forged_substantive":
        return FreezeAuthorization(
            state="absent",
            advisory=resolved.advisory or "forged_substantive_gate",
        )
    if resolved.kind == "unreadable":
        return FreezeAuthorization(
            state="absent",
            advisory=resolved.advisory or "unreadable_gate",
        )
    if resolved.kind == "mechanical":
        if resolved.verdict == "pass":
            return FreezeAuthorization(
                state="mechanical_only",
                advisory=advisory,
            )
        if resolved.verdict:
            return FreezeAuthorization(state="non_pass", advisory=advisory)
        return FreezeAuthorization(state="absent", advisory=advisory)

    return FreezeAuthorization(state="absent", advisory=advisory)

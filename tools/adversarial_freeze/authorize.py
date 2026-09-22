"""Shared AFF authorization helper (§AFF.5.6 / §AFF.7.1)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from adapters.config import OverseerConfig
from cli.paths import PathEscapeError, confine_path
from tools.freeze_authorization.resolve import freeze_authorization_state
from tools.freeze_reviewer.artifact import artifact_digest, parse_artifact
from tools.honesty.gate import honesty_module_disabled
from tools.honesty.ledger import verify_chain
from tools.honesty.ledger_io import read_ledger_entries
from tools.honesty.validate import find_latest_adversarial_freeze_verdict

AffAuthState = Literal["off", "pass", "skipped", "pending", "absent"]

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

_AGGREGATE_RANK = {
    "absent": 0,
    "pending": 1,
    "skipped": 2,
    "pass": 3,
}


@dataclass(frozen=True)
class AdversarialAuthorization:
    """Shared AFF authorization state for next_regen + status (§AFF.5.6)."""

    state: AffAuthState
    matched_entry_hash: str | None = None
    matched_via: str | None = None


def aff_hold_bypassed(config: OverseerConfig) -> bool:
    """True when honesty is disabled or resolved adversarial_freeze is off."""
    if honesty_module_disabled(config):
        return True
    return config.honesty.adversarial_freeze == "off"


def author_loop_complete(
    frv_state: str,
    *,
    stamp_digest: str | None,
    current_digest: str,
) -> bool:
    """Trigger-B fresh-stamp predicate (§AFF.7.1 ADV2-M1)."""
    if frv_state == "substantive":
        return True
    if frv_state == "mechanical_only":
        if not isinstance(stamp_digest, str) or not _DIGEST_RE.fullmatch(stamp_digest):
            return False
        return stamp_digest == current_digest
    return False


def frv_authorizing_freeze_paths(
    repo_root: Path,
    candidates: list[Path],
    *,
    phase_id: str,
    config: OverseerConfig,
) -> list[Path]:
    """Discover-order paths whose freeze_authorization_state is substantive."""
    authorizing: list[Path] = []
    for path in candidates:
        auth = freeze_authorization_state(
            repo_root, path, phase_id=phase_id, config=config
        )
        if auth.state == "substantive":
            authorizing.append(path)
    return authorizing


def aggregate_adversarial_authorization_states(states: list[str]) -> str:
    """Worst-state aggregate: absent > pending > skipped > pass (§AFF.5.6)."""
    ranked = [s for s in states if s in _AGGREGATE_RANK]
    if not ranked:
        raise ValueError("aggregate requires at least one non-off state")
    return min(ranked, key=lambda s: _AGGREGATE_RANK[s])


def adversarial_authorization_state(
    repo_root: Path,
    artifact_path: Path,
    *,
    config: OverseerConfig,
) -> AdversarialAuthorization:
    """Evaluate AFF authorization for a freeze artifact (§AFF.5.6)."""
    try:
        return _adversarial_authorization_state_impl(
            repo_root, artifact_path, config=config
        )
    except Exception:
        mode = config.honesty.adversarial_freeze
        if aff_hold_bypassed(config):
            return AdversarialAuthorization(state="off")
        if mode in {"suggest", "require"}:
            return AdversarialAuthorization(state="absent")
        return AdversarialAuthorization(state="off")


def _resolve_ledger_path_safe(config: OverseerConfig, repo_root: Path) -> Path | None:
    try:
        ledger = config.honesty.ledger
        if ledger is None or not str(ledger).strip():
            return None
        return confine_path(repo_root, str(ledger))
    except (PathEscapeError, ValueError, TypeError, AttributeError, OSError):
        return None


def _adversarial_authorization_state_impl(
    repo_root: Path,
    artifact_path: Path,
    *,
    config: OverseerConfig,
) -> AdversarialAuthorization:
    mode = config.honesty.adversarial_freeze
    if aff_hold_bypassed(config):
        return AdversarialAuthorization(state="off")

    try:
        rel = artifact_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return AdversarialAuthorization(state="absent")

    try:
        parsed = parse_artifact(artifact_path, rel_path=rel)
        digest = artifact_digest(parsed)
    except (ValueError, OSError, UnicodeError, Exception):
        return AdversarialAuthorization(state="absent")

    ledger_path = _resolve_ledger_path_safe(config, repo_root)
    if ledger_path is None or not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        return AdversarialAuthorization(state="pending")

    try:
        entries = read_ledger_entries(ledger_path)
    except (ValueError, OSError):
        return AdversarialAuthorization(state="absent")

    chain_code = verify_chain(
        entries,
        regime=config.vcs.regime,
        require_agent_signature=config.honesty.require_agent_signature,
    )
    if chain_code != 0:
        return AdversarialAuthorization(state="absent")

    winner = find_latest_adversarial_freeze_verdict(
        entries,
        frozen_spec=rel,
        artifact_digest=digest,
    )
    return _map_winner(winner, mode=mode)


def _map_winner(
    winner: dict | None,
    *,
    mode: str,
) -> AdversarialAuthorization:
    if winner is None:
        return AdversarialAuthorization(state="pending")
    verdict = winner.get("aff_verdict")
    entry_hash = winner.get("entry_hash")
    hash_s = entry_hash if isinstance(entry_hash, str) else None
    if verdict == "pass":
        return AdversarialAuthorization(
            state="pass", matched_entry_hash=hash_s, matched_via="pass"
        )
    if verdict == "skip":
        if mode == "suggest":
            return AdversarialAuthorization(
                state="skipped", matched_entry_hash=hash_s, matched_via="skip"
            )
        return AdversarialAuthorization(state="pending")
    # findings | blocked
    return AdversarialAuthorization(state="pending")

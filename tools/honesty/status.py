"""Honesty-status co-requirement check (§K9.8 / §PE.6 / §PD.5)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from adapters.config import OverseerConfig
from cli.paths import PathEscapeError, confine_path, repo_relative
from tools.freeze_reviewer.artifact import artifact_digest, parse_artifact
from tools.honesty.artifact import sha256_file_bytes
from tools.honesty.gate import check_roles_file, honesty_module_disabled, hook_enabled
from tools.honesty.ledger import verify_chain
from tools.honesty.ledger_io import read_ledger_entries
from tools.honesty.provenance import (
    provenance_has_signature,
    signature_required_for_kind,
    verify_entry_provenance,
)
from tools.honesty.types import HOOK_NAMES, HonestyStatusJson, HonestyStatusResult
from tools.honesty.validate import (
    find_latest_adversarial_freeze_verdict,
    find_matching_deploy_health,
    find_matching_independent_second_review,
    find_matching_verification_evidence,
)

EXIT_MISSING_INDEPENDENT_SECOND_REVIEW = 38
EXIT_MISSING_ADVERSARIAL_FREEZE = 40

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class HonestyStatusOptions:
    """CLI options for honesty-status."""

    hook: str | None
    artifact: str | None
    producer_session: str | None = None
    verification_evidence: str | None = None
    frozen_spec: str | None = None
    deploy_health: str | None = None
    independent_second_review: str | None = None
    adversarial_freeze: str | None = None
    artifact_digest: str | None = None
    emit_json: bool = False


def _usage_result(
    *,
    hook: str | None,
    artifact: str | None,
    producer_session: str | None,
    verification_evidence: dict[str, Any] | None = None,
    deploy_health: dict[str, Any] | None = None,
    independent_second_review: dict[str, Any] | None = None,
    adversarial_freeze: dict[str, Any] | None = None,
) -> HonestyStatusResult:
    payload = HonestyStatusJson(
        ok=False,
        exit_code=1,
        hook=hook,
        artifact=artifact,
        producer_session=producer_session,
        error="usage",
        verification_evidence=verification_evidence,
        deploy_health=deploy_health,
        independent_second_review=independent_second_review,
        adversarial_freeze=adversarial_freeze,
    )
    return HonestyStatusResult(exit_code=1, json_payload=payload)


def _mode_b_block(
    *,
    phase_id: str,
    frozen_spec: str | None,
    require: str,
    matched_entry_hash: str | None,
) -> dict[str, Any]:
    return {
        "phase_id": phase_id,
        "frozen_spec": frozen_spec,
        "require": require,
        "matched_entry_hash": matched_entry_hash,
    }


def _mode_c_block(
    *,
    phase_id: str,
    frozen_spec: str | None,
    require: str,
    matched_entry_hash: str | None,
) -> dict[str, Any]:
    return {
        "phase_id": phase_id,
        "frozen_spec": frozen_spec,
        "require": require,
        "matched_entry_hash": matched_entry_hash,
    }


def _mode_d_block(
    *,
    phase_id: str,
    frozen_spec: str | None,
    producer_session: str | None,
    require: str,
    matched_entry_hash: str | None,
) -> dict[str, Any]:
    return {
        "phase_id": phase_id,
        "frozen_spec": frozen_spec,
        "producer_session": producer_session,
        "require": require,
        "matched_entry_hash": matched_entry_hash,
    }


def _mode_e_block(
    *,
    phase_id: str,
    frozen_spec: str | None,
    artifact_digest: str | None,
    producer_session: str | None,
    mode: str,
    matched_via: str | None,
    matched_entry_hash: str | None,
) -> dict[str, Any]:
    return {
        "phase_id": phase_id,
        "frozen_spec": frozen_spec,
        "artifact_digest": artifact_digest,
        "producer_session": producer_session,
        "mode": mode,
        "matched_via": matched_via,
        "matched_entry_hash": matched_entry_hash,
    }


def _has_l1_evidence(entry: dict[str, Any]) -> bool:
    evidence = entry.get("evidence")
    if not isinstance(evidence, dict):
        return False
    reexecuted = evidence.get("reexecuted")
    if not isinstance(reexecuted, list):
        return False
    prefix = "verify-step:"
    return any(isinstance(item, str) and item.startswith(prefix) for item in reexecuted)


def _match_verdicts(
    entries: list[dict[str, Any]],
    *,
    artifact_sha256: str,
    producer_session: str | None,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("kind") != "verdict":
            continue
        if entry.get("passed") is not True:
            continue
        if entry.get("actor_role") != "verifier":
            continue
        if entry.get("artifact_sha256") != artifact_sha256:
            continue
        if producer_session is not None and entry.get("actor_session_id") == producer_session:
            continue
        matches.append(entry)
    return matches


def _resolve_mode(options: HonestyStatusOptions) -> str | None:
    """Return ``mode_a``–``mode_e``, or ``None`` when usage is invalid (§AFF.8.2)."""
    hook = options.hook
    artifact = options.artifact
    producer = options.producer_session is not None
    mode_a_core = bool(hook or artifact)
    mode_a_full = bool(hook and artifact)
    mode_b_full = options.verification_evidence is not None
    mode_c_full = options.deploy_health is not None
    mode_d_full = options.independent_second_review is not None
    mode_e_full = options.adversarial_freeze is not None
    frozen = options.frozen_spec is not None
    digest = options.artifact_digest is not None

    mode_a_partial = mode_a_core or (
        producer and not mode_d_full and not mode_e_full
    )

    if digest and not mode_e_full:
        return None
    if mode_e_full and digest and not frozen:
        return None
    if (int(mode_b_full) + int(mode_c_full) + int(mode_d_full) + int(mode_e_full)) > 1:
        return None
    if mode_a_partial and (
        mode_b_full or mode_c_full or mode_d_full or mode_e_full or frozen
    ):
        return None
    if frozen and not mode_b_full and not mode_c_full and not mode_d_full and not mode_e_full:
        return None
    if (
        not mode_a_full
        and not mode_b_full
        and not mode_c_full
        and not mode_d_full
        and not mode_e_full
    ):
        return None
    if mode_e_full:
        return "mode_e"
    if mode_d_full:
        return "mode_d"
    if mode_c_full:
        return "mode_c"
    if mode_b_full:
        return "mode_b"
    return "mode_a"


def _run_mode_c(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> HonestyStatusResult:
    phase_id = options.deploy_health
    frozen_spec = options.frozen_spec
    require = config.honesty.require_deploy_health
    assert phase_id is not None

    block = _mode_c_block(
        phase_id=phase_id,
        frozen_spec=frozen_spec,
        require=require,
        matched_entry_hash=None,
    )

    if honesty_module_disabled(config):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            deploy_health=block,
        )
        return HonestyStatusResult(
            exit_code=4,
            json_payload=payload,
            stderr_extra="refused: honesty.enabled is false",
        )

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            deploy_health=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    try:
        ledger_rel = config.honesty.ledger
        if ledger_rel is None or not ledger_rel.strip():
            raise ValueError("missing ledger")
        ledger_path = confine_path(repo_root, ledger_rel)
    except Exception:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            deploy_health=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        if require == "require":
            block["matched_entry_hash"] = None
            payload = HonestyStatusJson(
                ok=False,
                exit_code=34,
                error="missing_deploy_health",
                deploy_health=block,
            )
            return HonestyStatusResult(exit_code=34, json_payload=payload, stderr_extra=roles_warn or "")
        warn_msg = ""
        if require == "warn":
            warn_msg = "warning: no matching deploy_health evidence entry"
        block["matched_entry_hash"] = None
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            error=None,
            deploy_health=block,
        )
        stderr_parts = [part for part in (roles_warn, warn_msg) if part]
        return HonestyStatusResult(
            exit_code=0,
            json_payload=payload,
            stderr_extra="\n".join(stderr_parts),
        )

    try:
        entries = read_ledger_entries(ledger_path)
    except (ValueError, OSError):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            deploy_health=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    winner = find_matching_deploy_health(
        entries,
        phase_id=phase_id,
        frozen_spec=frozen_spec,
    )

    if winner is None:
        if require == "require":
            block["matched_entry_hash"] = None
            payload = HonestyStatusJson(
                ok=False,
                exit_code=34,
                error="missing_deploy_health",
                deploy_health=block,
            )
            return HonestyStatusResult(exit_code=34, json_payload=payload, stderr_extra=roles_warn or "")
        warn_msg = ""
        if require == "warn":
            warn_msg = "warning: no matching deploy_health evidence entry"
        block["matched_entry_hash"] = None
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            error=None,
            deploy_health=block,
        )
        stderr_parts = [part for part in (roles_warn, warn_msg) if part]
        return HonestyStatusResult(
            exit_code=0,
            json_payload=payload,
            stderr_extra="\n".join(stderr_parts),
        )

    matched_hash = winner.get("entry_hash")
    block["matched_entry_hash"] = matched_hash if isinstance(matched_hash, str) else None
    payload = HonestyStatusJson(
        ok=True,
        exit_code=0,
        error=None,
        deploy_health=block,
    )
    return HonestyStatusResult(
        exit_code=0,
        json_payload=payload,
        stderr_extra=roles_warn or "",
    )


def _run_mode_b(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> HonestyStatusResult:
    phase_id = options.verification_evidence
    frozen_spec = options.frozen_spec
    require = config.honesty.require_verification_evidence
    assert phase_id is not None

    block = _mode_b_block(
        phase_id=phase_id,
        frozen_spec=frozen_spec,
        require=require,
        matched_entry_hash=None,
    )

    if honesty_module_disabled(config):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            verification_evidence=block,
        )
        return HonestyStatusResult(
            exit_code=4,
            json_payload=payload,
            stderr_extra="refused: honesty.enabled is false",
        )

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            verification_evidence=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    try:
        ledger_rel = config.honesty.ledger
        if ledger_rel is None or not ledger_rel.strip():
            raise ValueError("missing ledger")
        ledger_path = confine_path(repo_root, ledger_rel)
    except Exception:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            verification_evidence=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        if require == "require":
            block["matched_entry_hash"] = None
            payload = HonestyStatusJson(
                ok=False,
                exit_code=33,
                error="missing_verification_evidence",
                verification_evidence=block,
            )
            return HonestyStatusResult(exit_code=33, json_payload=payload, stderr_extra=roles_warn or "")
        warn_msg = ""
        if require == "warn":
            warn_msg = "warning: no matching verification_evidence entry"
        block["matched_entry_hash"] = None
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            error=None,
            verification_evidence=block,
        )
        stderr_parts = [part for part in (roles_warn, warn_msg) if part]
        return HonestyStatusResult(
            exit_code=0,
            json_payload=payload,
            stderr_extra="\n".join(stderr_parts),
        )

    try:
        entries = read_ledger_entries(ledger_path)
    except (ValueError, OSError):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            error="refused",
            verification_evidence=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    winner = find_matching_verification_evidence(
        entries,
        phase_id=phase_id,
        frozen_spec=frozen_spec,
    )

    if winner is None:
        if require == "require":
            block["matched_entry_hash"] = None
            payload = HonestyStatusJson(
                ok=False,
                exit_code=33,
                error="missing_verification_evidence",
                verification_evidence=block,
            )
            return HonestyStatusResult(exit_code=33, json_payload=payload, stderr_extra=roles_warn or "")
        warn_msg = ""
        if require == "warn":
            warn_msg = "warning: no matching verification_evidence entry"
        block["matched_entry_hash"] = None
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            error=None,
            verification_evidence=block,
        )
        stderr_parts = [part for part in (roles_warn, warn_msg) if part]
        return HonestyStatusResult(
            exit_code=0,
            json_payload=payload,
            stderr_extra="\n".join(stderr_parts),
        )

    matched_hash = winner.get("entry_hash")
    block["matched_entry_hash"] = matched_hash if isinstance(matched_hash, str) else None
    payload = HonestyStatusJson(
        ok=True,
        exit_code=0,
        error=None,
        verification_evidence=block,
    )
    return HonestyStatusResult(
        exit_code=0,
        json_payload=payload,
        stderr_extra=roles_warn or "",
    )


def _run_mode_d(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> HonestyStatusResult:
    phase_id = options.independent_second_review
    frozen_spec = options.frozen_spec
    producer_session = options.producer_session
    require = config.honesty.require_independent_second_reviewer
    assert phase_id is not None

    block = _mode_d_block(
        phase_id=phase_id,
        frozen_spec=frozen_spec,
        producer_session=producer_session,
        require=require,
        matched_entry_hash=None,
    )

    if honesty_module_disabled(config):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            independent_second_review=block,
        )
        return HonestyStatusResult(
            exit_code=4,
            json_payload=payload,
            stderr_extra="refused: honesty.enabled is false",
        )

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            independent_second_review=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    try:
        ledger_rel = config.honesty.ledger
        if ledger_rel is None or not ledger_rel.strip():
            raise ValueError("missing ledger")
        ledger_path = confine_path(repo_root, ledger_rel)
    except Exception:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            independent_second_review=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        if require == "require":
            payload = HonestyStatusJson(
                ok=False,
                exit_code=EXIT_MISSING_INDEPENDENT_SECOND_REVIEW,
                producer_session=producer_session,
                error="missing_independent_second_review",
                independent_second_review=block,
            )
            return HonestyStatusResult(
                exit_code=EXIT_MISSING_INDEPENDENT_SECOND_REVIEW,
                json_payload=payload,
                stderr_extra=roles_warn or "",
            )
        warn_msg = ""
        if require == "warn":
            warn_msg = "warning: no matching independent_second_review entry"
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            producer_session=producer_session,
            error=None,
            independent_second_review=block,
        )
        stderr_parts = [part for part in (roles_warn, warn_msg) if part]
        return HonestyStatusResult(
            exit_code=0,
            json_payload=payload,
            stderr_extra="\n".join(stderr_parts),
        )

    try:
        entries = read_ledger_entries(ledger_path)
    except (ValueError, OSError):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            independent_second_review=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    winner = find_matching_independent_second_review(
        entries,
        phase_id=phase_id,
        frozen_spec=frozen_spec,
        producer_session=producer_session,
    )

    if winner is None:
        if require == "require":
            payload = HonestyStatusJson(
                ok=False,
                exit_code=EXIT_MISSING_INDEPENDENT_SECOND_REVIEW,
                producer_session=producer_session,
                error="missing_independent_second_review",
                independent_second_review=block,
            )
            return HonestyStatusResult(
                exit_code=EXIT_MISSING_INDEPENDENT_SECOND_REVIEW,
                json_payload=payload,
                stderr_extra=roles_warn or "",
            )
        warn_msg = ""
        if require == "warn":
            warn_msg = "warning: no matching independent_second_review entry"
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            producer_session=producer_session,
            error=None,
            independent_second_review=block,
        )
        stderr_parts = [part for part in (roles_warn, warn_msg) if part]
        return HonestyStatusResult(
            exit_code=0,
            json_payload=payload,
            stderr_extra="\n".join(stderr_parts),
        )

    matched_hash = winner.get("entry_hash")
    block["matched_entry_hash"] = matched_hash if isinstance(matched_hash, str) else None
    payload = HonestyStatusJson(
        ok=True,
        exit_code=0,
        producer_session=producer_session,
        error=None,
        independent_second_review=block,
    )
    return HonestyStatusResult(
        exit_code=0,
        json_payload=payload,
        stderr_extra=roles_warn or "",
    )


def _run_mode_a(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> HonestyStatusResult:
    """Evaluate co-requirement for a hook + artifact pair (unchanged from pre-P-evidence)."""
    hook = options.hook
    artifact = options.artifact

    if not hook or not artifact:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=1,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="usage",
        )
        return HonestyStatusResult(exit_code=1, json_payload=payload)

    if hook not in HOOK_NAMES:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=1,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="usage",
        )
        return HonestyStatusResult(exit_code=1, json_payload=payload)

    if honesty_module_disabled(config):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(
            exit_code=4,
            json_payload=payload,
            stderr_extra="refused: honesty.enabled is false",
        )

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    if not hook_enabled(config, hook):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(
            exit_code=4,
            json_payload=payload,
            stderr_extra=f"refused: hook {hook!r} not enabled for co-requirement",
        )

    try:
        ledger_rel = config.honesty.ledger
        if ledger_rel is None or not ledger_rel.strip():
            raise ValueError("missing ledger")
        ledger_path = confine_path(repo_root, ledger_rel)
    except Exception:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    try:
        artifact_path = confine_path(repo_root, artifact)
    except Exception:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    if not artifact_path.is_file():
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    artifact_rel = repo_relative(repo_root, artifact_path)
    try:
        artifact_sha256 = sha256_file_bytes(artifact_path)
    except OSError:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact_rel,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=20,
            hook=hook,
            artifact=artifact_rel,
            artifact_sha256=artifact_sha256,
            producer_session=options.producer_session,
            matched_verdict_hash=None,
            error="missing_verdict",
        )
        stderr = roles_warn or ""
        return HonestyStatusResult(exit_code=20, json_payload=payload, stderr_extra=stderr)

    try:
        entries = read_ledger_entries(ledger_path)
    except (ValueError, OSError):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            hook=hook,
            artifact=artifact_rel,
            artifact_sha256=artifact_sha256,
            producer_session=options.producer_session,
            error="refused",
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    matches = _match_verdicts(
        entries,
        artifact_sha256=artifact_sha256,
        producer_session=options.producer_session,
    )

    if not matches:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=20,
            hook=hook,
            artifact=artifact_rel,
            artifact_sha256=artifact_sha256,
            producer_session=options.producer_session,
            matched_verdict_hash=None,
            error="missing_verdict",
        )
        return HonestyStatusResult(exit_code=20, json_payload=payload, stderr_extra=roles_warn or "")

    winner = matches[-1]
    matched_hash = winner.get("entry_hash")

    if signature_required_for_kind(
        require_agent_signature=config.honesty.require_agent_signature,
        kind=str(winner.get("kind", "")),
    ) and not provenance_has_signature(winner):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=26,
            hook=hook,
            artifact=artifact_rel,
            artifact_sha256=artifact_sha256,
            producer_session=options.producer_session,
            matched_verdict_hash=matched_hash if isinstance(matched_hash, str) else None,
            error="refused",
        )
        return HonestyStatusResult(
            exit_code=26,
            json_payload=payload,
            stderr_extra=roles_warn or "",
        )

    sig_code = verify_entry_provenance(winner, regime=config.vcs.regime)
    if sig_code != 0:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=sig_code,
            hook=hook,
            artifact=artifact_rel,
            artifact_sha256=artifact_sha256,
            producer_session=options.producer_session,
            matched_verdict_hash=matched_hash if isinstance(matched_hash, str) else None,
            error="refused",
        )
        return HonestyStatusResult(
            exit_code=sig_code,
            json_payload=payload,
            stderr_extra=roles_warn or "",
        )

    mode = config.honesty.require_l1_evidence
    warn_msg = ""
    if mode in {"warn", "require"} and not _has_l1_evidence(winner):
        if mode == "require":
            payload = HonestyStatusJson(
                ok=False,
                exit_code=20,
                hook=hook,
                artifact=artifact_rel,
                artifact_sha256=artifact_sha256,
                producer_session=options.producer_session,
                matched_verdict_hash=matched_hash if isinstance(matched_hash, str) else None,
                error="missing_verdict",
            )
            return HonestyStatusResult(exit_code=20, json_payload=payload, stderr_extra=roles_warn or "")
        warn_msg = "warning: matched verdict lacks verify-step: L1 evidence"

    stderr_parts = [part for part in (roles_warn, warn_msg) if part]
    payload = HonestyStatusJson(
        ok=True,
        exit_code=0,
        hook=hook,
        artifact=artifact_rel,
        artifact_sha256=artifact_sha256,
        producer_session=options.producer_session,
        matched_verdict_hash=matched_hash if isinstance(matched_hash, str) else None,
        error=None,
    )
    return HonestyStatusResult(
        exit_code=0,
        json_payload=payload,
        stderr_extra="\n".join(stderr_parts),
    )


def run_honesty_status(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> HonestyStatusResult:
    """Evaluate honesty-status in Mode A, B, C, D, or E."""
    mode = _resolve_mode(options)
    if mode is None:
        verification_block = None
        deploy_block = None
        isr_block = None
        aff_block = None
        if options.verification_evidence:
            verification_block = _mode_b_block(
                phase_id=options.verification_evidence,
                frozen_spec=options.frozen_spec,
                require=config.honesty.require_verification_evidence,
                matched_entry_hash=None,
            )
        if options.deploy_health:
            deploy_block = _mode_c_block(
                phase_id=options.deploy_health,
                frozen_spec=options.frozen_spec,
                require=config.honesty.require_deploy_health,
                matched_entry_hash=None,
            )
        if options.independent_second_review:
            isr_block = _mode_d_block(
                phase_id=options.independent_second_review,
                frozen_spec=options.frozen_spec,
                producer_session=options.producer_session,
                require=config.honesty.require_independent_second_reviewer,
                matched_entry_hash=None,
            )
        if options.adversarial_freeze:
            aff_block = _mode_e_block(
                phase_id=options.adversarial_freeze,
                frozen_spec=None,
                artifact_digest=None,
                producer_session=options.producer_session,
                mode=config.honesty.adversarial_freeze,
                matched_via=None,
                matched_entry_hash=None,
            )
        return _usage_result(
            hook=options.hook,
            artifact=options.artifact,
            producer_session=options.producer_session,
            verification_evidence=verification_block,
            deploy_health=deploy_block,
            independent_second_review=isr_block,
            adversarial_freeze=aff_block,
        )

    if mode == "mode_e":
        return _run_mode_e(config=config, repo_root=repo_root, options=options)
    if mode == "mode_d":
        return _run_mode_d(config=config, repo_root=repo_root, options=options)
    if mode == "mode_c":
        return _run_mode_c(config=config, repo_root=repo_root, options=options)
    if mode == "mode_b":
        return _run_mode_b(config=config, repo_root=repo_root, options=options)
    return _run_mode_a(config=config, repo_root=repo_root, options=options)


def _resolve_mode_e_path_digest(
    *,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> tuple[str | None, str | None, int | None]:
    """Return ``(frozen_spec, artifact_digest, refuse_exit)`` for Mode E (§AFF.8.1).

    ``refuse_exit`` is ``4`` on path escape/I/O, ``1`` on digest usage errors,
    or ``None`` when resolution succeeded (including fail-closed miss with nulls).
    """
    import stat as stat_mod

    frozen_flag = options.frozen_spec
    digest_flag = options.artifact_digest
    effective_digest: str | None = None

    if digest_flag is not None:
        if not isinstance(digest_flag, str) or not _DIGEST_RE.fullmatch(digest_flag):
            return None, None, 1
        effective_digest = digest_flag

    if frozen_flag is None:
        return None, effective_digest, None

    try:
        confined = confine_path(repo_root, frozen_flag)
        effective_path = repo_relative(repo_root, confined)
    except PathEscapeError:
        return None, None, 4
    except OSError:
        return None, None, 4

    try:
        exists = confined.exists()
    except OSError:
        return None, None, 4

    if not exists:
        return effective_path, effective_digest, None

    try:
        st = confined.stat()
        is_regular = stat_mod.S_ISREG(st.st_mode)
    except OSError:
        return None, None, 4

    if is_regular:
        try:
            parsed = parse_artifact(confined, rel_path=effective_path)
            hashed = artifact_digest(parsed)
        except (ValueError, OSError, UnicodeError):
            if effective_digest is None:
                return effective_path, None, None
            return None, None, 1
        if effective_digest is None:
            return effective_path, hashed, None
        if hashed != effective_digest:
            return None, None, 1
        return effective_path, effective_digest, None

    # Existing non-regular path: explicit digest → ledger query; else miss.
    if effective_digest is not None:
        return effective_path, effective_digest, None
    return effective_path, None, None


def _run_mode_e(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> HonestyStatusResult:
    phase_id = options.adversarial_freeze
    producer_session = options.producer_session
    mode = config.honesty.adversarial_freeze
    assert phase_id is not None

    # Digest shape check before path work when flag present and mode resolved.
    if options.artifact_digest is not None and (
        not isinstance(options.artifact_digest, str)
        or not _DIGEST_RE.fullmatch(options.artifact_digest)
    ):
        block = _mode_e_block(
            phase_id=phase_id,
            frozen_spec=None,
            artifact_digest=None,
            producer_session=producer_session,
            mode=mode,
            matched_via=None,
            matched_entry_hash=None,
        )
        return _usage_result(
            hook=None,
            artifact=None,
            producer_session=producer_session,
            adversarial_freeze=block,
        )

    frozen_spec, artifact_digest_val, refuse = _resolve_mode_e_path_digest(
        repo_root=repo_root, options=options
    )
    if refuse == 1:
        block = _mode_e_block(
            phase_id=phase_id,
            frozen_spec=None,
            artifact_digest=None,
            producer_session=producer_session,
            mode=mode,
            matched_via=None,
            matched_entry_hash=None,
        )
        return _usage_result(
            hook=None,
            artifact=None,
            producer_session=producer_session,
            adversarial_freeze=block,
        )

    block = _mode_e_block(
        phase_id=phase_id,
        frozen_spec=frozen_spec,
        artifact_digest=artifact_digest_val,
        producer_session=producer_session,
        mode=mode,
        matched_via=None,
        matched_entry_hash=None,
    )

    if refuse == 4 or honesty_module_disabled(config):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            adversarial_freeze=block,
        )
        return HonestyStatusResult(
            exit_code=4,
            json_payload=payload,
            stderr_extra="refused: honesty.enabled is false"
            if honesty_module_disabled(config)
            else "refused",
        )

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            adversarial_freeze=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    # Mode off: exact block, no ledger read.
    if mode == "off":
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            producer_session=producer_session,
            error=None,
            adversarial_freeze=block,
        )
        return HonestyStatusResult(
            exit_code=0,
            json_payload=payload,
            stderr_extra=roles_warn or "",
        )

    # Fail-closed miss when effective path or digest is null.
    if frozen_spec is None or artifact_digest_val is None:
        return _mode_e_miss(
            block=block,
            mode=mode,
            producer_session=producer_session,
            roles_warn=roles_warn,
        )

    try:
        ledger_rel = config.honesty.ledger
        if ledger_rel is None or not ledger_rel.strip():
            raise ValueError("missing ledger")
        ledger_path = confine_path(repo_root, ledger_rel)
    except Exception:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            adversarial_freeze=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        return _mode_e_miss(
            block=block,
            mode=mode,
            producer_session=producer_session,
            roles_warn=roles_warn,
        )

    try:
        entries = read_ledger_entries(ledger_path)
    except (ValueError, OSError):
        payload = HonestyStatusJson(
            ok=False,
            exit_code=4,
            producer_session=producer_session,
            error="refused",
            adversarial_freeze=block,
        )
        return HonestyStatusResult(exit_code=4, json_payload=payload)

    chain_code = verify_chain(
        entries,
        regime=config.vcs.regime,
        require_agent_signature=config.honesty.require_agent_signature,
    )
    if chain_code == 22:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=22,
            producer_session=producer_session,
            error="ledger_broken",
            adversarial_freeze=block,
        )
        return HonestyStatusResult(exit_code=22, json_payload=payload, stderr_extra=roles_warn or "")
    if chain_code in {2, 25, 26}:
        payload = HonestyStatusJson(
            ok=False,
            exit_code=chain_code,
            producer_session=producer_session,
            error="refused",
            adversarial_freeze=block,
        )
        return HonestyStatusResult(
            exit_code=chain_code, json_payload=payload, stderr_extra=roles_warn or ""
        )

    winner = find_latest_adversarial_freeze_verdict(
        entries,
        frozen_spec=frozen_spec,
        artifact_digest=artifact_digest_val,
        phase_id=phase_id,
        producer_session=producer_session,
    )

    authorizing = False
    matched_via: str | None = None
    matched_hash: str | None = None
    if winner is not None:
        verdict = winner.get("aff_verdict")
        if verdict == "pass":
            authorizing = True
            matched_via = "pass"
            mh = winner.get("entry_hash")
            matched_hash = mh if isinstance(mh, str) else None
        elif verdict == "skip" and mode == "suggest":
            authorizing = True
            matched_via = "skip"
            mh = winner.get("entry_hash")
            matched_hash = mh if isinstance(mh, str) else None

    if authorizing:
        block["matched_via"] = matched_via
        block["matched_entry_hash"] = matched_hash
        payload = HonestyStatusJson(
            ok=True,
            exit_code=0,
            producer_session=producer_session,
            error=None,
            adversarial_freeze=block,
        )
        return HonestyStatusResult(
            exit_code=0, json_payload=payload, stderr_extra=roles_warn or ""
        )

    return _mode_e_miss(
        block=block,
        mode=mode,
        producer_session=producer_session,
        roles_warn=roles_warn,
    )


def _mode_e_miss(
    *,
    block: dict[str, Any],
    mode: str,
    producer_session: str | None,
    roles_warn: str | None,
) -> HonestyStatusResult:
    if mode == "require":
        payload = HonestyStatusJson(
            ok=False,
            exit_code=EXIT_MISSING_ADVERSARIAL_FREEZE,
            producer_session=producer_session,
            error="missing_adversarial_freeze",
            adversarial_freeze=block,
        )
        return HonestyStatusResult(
            exit_code=EXIT_MISSING_ADVERSARIAL_FREEZE,
            json_payload=payload,
            stderr_extra=roles_warn or "",
        )
    warn_msg = ""
    if mode == "suggest":
        warn_msg = "warning: no authorizing adversarial_freeze entry"
    payload = HonestyStatusJson(
        ok=True,
        exit_code=0,
        producer_session=producer_session,
        error=None,
        adversarial_freeze=block,
    )
    stderr_parts = [part for part in (roles_warn, warn_msg) if part]
    return HonestyStatusResult(
        exit_code=0,
        json_payload=payload,
        stderr_extra="\n".join(stderr_parts),
    )

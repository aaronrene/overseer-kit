"""Honesty-status co-requirement check (§K9.8)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from adapters.config import OverseerConfig
from cli.paths import confine_path, repo_relative
from tools.honesty.artifact import sha256_file_bytes
from tools.honesty.gate import check_roles_file, honesty_module_disabled, hook_enabled
from tools.honesty.ledger_io import read_ledger_entries
from tools.honesty.types import HOOK_NAMES, HonestyStatusJson, HonestyStatusResult


@dataclass(frozen=True)
class HonestyStatusOptions:
    """CLI options for honesty-status."""

    hook: str | None
    artifact: str | None
    producer_session: str | None = None
    emit_json: bool = False


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


def run_honesty_status(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: HonestyStatusOptions,
) -> HonestyStatusResult:
    """Evaluate co-requirement for a hook + artifact pair."""
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

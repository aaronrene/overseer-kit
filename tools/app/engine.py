"""Thin HTTP handlers that call existing CLI engine functions (§Q0.7.1)."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from typing import Any

from cli.commands.governance_sync import run_governance_sync_command
from cli.commands.review import run_review
from cli.commands.status import run_status
from cli.context import CliContext
from tools.app.capture import CapturingOutputContext
from tools.app.docs import load_repo_config, read_handover, read_roadmap, resolve_app_repo
from tools.app.envelope import ApiEnvelope, bad_request, engine_failure, engine_success
from tools.honesty.ledger import append_entry, show_entries, verify_ledger_file
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import ENTRY_KINDS, LedgerAppendOptions


def _unknown_keys(body: dict[str, Any], allowed: frozenset[str]) -> list[str]:
    return sorted(key for key in body if key not in allowed)


def handle_health(*, port: int, bind: str, repo_root: Path | str) -> ApiEnvelope:
    """Process liveness endpoint with bound checkout path (§LAC.6.3).

    ``repo_root`` is the absolute filesystem path this process mutates — not a
    credential and not living-doc contents. Auth remains Bearer-gated (Q0 §Q0.6).
    """
    root = Path(repo_root).resolve()
    return engine_success(
        {
            "status": "ok",
            "port": port,
            "bind": bind,
            "repo_root": str(root),
        }
    )


def handle_status(ctx: CliContext, *, repo_arg: str | None = None) -> ApiEnvelope:
    """Mirror ``overseer status --json`` and always compute exit-code conditions."""
    repo_root = resolve_app_repo(ctx.cwd, repo_arg)

    capture = CapturingOutputContext()
    app_ctx = CliContext(
        kit=ctx.kit,
        runner=ctx.runner,
        output=capture,
        cwd=ctx.cwd,
        review_provider_factory=ctx.review_provider_factory,
        script_executor=ctx.script_executor,
    )
    args = Namespace(
        repo=repo_arg,
        config=None,
        exit_code=True,
        check_footprint=False,
    )
    exit_code = run_status(args, app_ctx)
    payload = capture.json_payload or {}
    return ApiEnvelope(
        ok=exit_code == 0,
        exit_code=exit_code,
        error=None if exit_code == 0 else _status_error_token(payload),
        result=payload,
        http_status=200,
    )


def _status_error_token(payload: dict[str, Any]) -> str | None:
    if payload.get("error"):
        return "config"
    substrate = payload.get("substrate") or {}
    if substrate.get("ok") is False:
        return "substrate"
    muse_sync = payload.get("muse_sync") or {}
    if muse_sync.get("ok") is False:
        return "muse_sync"
    footprint = payload.get("footprint_self_integrity") or {}
    if footprint.get("ok") is False:
        return "footprint_self_integrity"
    if payload.get("footprint_integrity") == "mismatch":
        return "footprint_integrity"
    drift = payload.get("drift") or {}
    if drift.get("status") in {"behind", "ahead"}:
        return "drift"
    return "status"


def handle_gates(ctx: CliContext, *, repo_arg: str | None = None) -> ApiEnvelope:
    """Return the pending-gates slice already embedded in status JSON."""
    status = handle_status(ctx, repo_arg=repo_arg)
    if status.result is None or not isinstance(status.result, dict):
        return status
    gates = status.result.get("governance_gates")
    return ApiEnvelope(
        ok=status.ok,
        exit_code=status.exit_code,
        error=status.error,
        result=gates,
        http_status=status.http_status,
    )


def handle_docs_roadmap(ctx: CliContext, *, repo_arg: str | None = None) -> ApiEnvelope:
    repo_root = resolve_app_repo(ctx.cwd, repo_arg)
    if not (repo_root / ".overseer").is_dir():
        return engine_failure(exit_code=2, error="config", result=None)
    config, config_refusal = load_repo_config(repo_root)
    if config_refusal is not None or config is None:
        return config_refusal or engine_failure(exit_code=2, error="config", result=None)
    return read_roadmap(repo_root=repo_root, config=config)


def handle_docs_handover(ctx: CliContext, *, repo_arg: str | None = None) -> ApiEnvelope:
    repo_root = resolve_app_repo(ctx.cwd, repo_arg)
    if not (repo_root / ".overseer").is_dir():
        return engine_failure(exit_code=2, error="config", result=None)
    config, config_refusal = load_repo_config(repo_root)
    if config_refusal is not None or config is None:
        return config_refusal or engine_failure(exit_code=2, error="config", result=None)
    return read_handover(repo_root=repo_root, config=config)


def handle_review_freeze(
    ctx: CliContext,
    body: dict[str, Any],
    *,
    repo_arg: str | None = None,
) -> ApiEnvelope:
    allowed = frozenset({"path", "dry_run", "no_stamp"})
    unknown = _unknown_keys(body, allowed)
    if unknown:
        return bad_request("unknown_fields")

    path = body.get("path")
    if not isinstance(path, str) or not path.strip():
        return bad_request("path_required")

    dry_run = body.get("dry_run", True)
    no_stamp = body.get("no_stamp", False)
    if not isinstance(dry_run, bool) or not isinstance(no_stamp, bool):
        return bad_request("invalid_boolean")

    capture = CapturingOutputContext()
    app_ctx = CliContext(
        kit=ctx.kit,
        runner=ctx.runner,
        output=capture,
        cwd=ctx.cwd,
        review_provider_factory=ctx.review_provider_factory,
        script_executor=ctx.script_executor,
    )
    args = Namespace(
        repo=repo_arg,
        config=None,
        freeze_path=path,
        dry_run=dry_run,
        no_stamp=no_stamp,
        mode=None,
        provider=None,
        model=None,
        checklist=None,
    )
    exit_code = run_review(args, app_ctx)
    result = capture.json_payload
    return ApiEnvelope(
        ok=exit_code == 0,
        exit_code=exit_code,
        error=_review_error_token(exit_code),
        result=result,
        http_status=200,
    )


def _review_error_token(exit_code: int) -> str | None:
    if exit_code == 0:
        return None
    if exit_code in {7, 8}:
        return "review"
    if exit_code == 4:
        return "path"
    if exit_code == 2:
        return "gate"
    return "review"


def handle_governance_sync(
    ctx: CliContext,
    body: dict[str, Any],
    *,
    repo_arg: str | None = None,
) -> ApiEnvelope:
    allowed = frozenset({"write"})
    unknown = _unknown_keys(body, allowed)
    if unknown:
        return bad_request("unknown_fields")

    write = body.get("write", False)
    if not isinstance(write, bool):
        return bad_request("invalid_boolean")

    capture = CapturingOutputContext()
    app_ctx = CliContext(
        kit=ctx.kit,
        runner=ctx.runner,
        output=capture,
        cwd=ctx.cwd,
        review_provider_factory=ctx.review_provider_factory,
        script_executor=ctx.script_executor,
    )
    args = Namespace(
        repo=repo_arg,
        config=None,
        write=write,
        dry_run=not write,
        lane=None,
        all_lanes=False,
    )
    exit_code = run_governance_sync_command(args, app_ctx)
    result = capture.json_payload
    return ApiEnvelope(
        ok=exit_code == 0,
        exit_code=exit_code,
        error=_governance_sync_error_token(exit_code),
        result=result,
        http_status=200,
    )


def _governance_sync_error_token(exit_code: int) -> str | None:
    if exit_code == 0:
        return None
    if exit_code == 2:
        return "gate"
    if exit_code == 4:
        return "path"
    return "governance_sync"


def handle_ledger_show(
    ctx: CliContext,
    *,
    last: int | None = None,
    repo_arg: str | None = None,
) -> ApiEnvelope:
    repo_root = resolve_app_repo(ctx.cwd, repo_arg)
    if not (repo_root / ".overseer").is_dir():
        return engine_failure(exit_code=2, error="config", result=None)

    config, config_refusal = load_repo_config(repo_root)
    if config_refusal is not None or config is None:
        return config_refusal or engine_failure(exit_code=2, error="config", result=None)

    last_n = 20 if last is None else last
    result = show_entries(config=config, repo_root=repo_root, last_n=last_n)
    entries = [json.loads(line) for line in result.stdout_lines]
    return ApiEnvelope(
        ok=result.exit_code == 0,
        exit_code=result.exit_code,
        error=_ledger_error_token(result.exit_code),
        result={"entries": entries, "lines": result.stdout_lines},
        http_status=200,
    )


def handle_ledger_verify(ctx: CliContext, body: dict[str, Any], *, repo_arg: str | None = None) -> ApiEnvelope:
    if body and _unknown_keys(body, frozenset()):
        return bad_request("unknown_fields")

    repo_root = resolve_app_repo(ctx.cwd, repo_arg)
    if not (repo_root / ".overseer").is_dir():
        return engine_failure(exit_code=2, error="config", result=None)

    config, config_refusal = load_repo_config(repo_root)
    if config_refusal is not None or config is None:
        return config_refusal or engine_failure(exit_code=2, error="config", result=None)

    result = verify_ledger_file(config=config, repo_root=repo_root)
    return ApiEnvelope(
        ok=result.exit_code == 0,
        exit_code=result.exit_code,
        error=_ledger_error_token(result.exit_code),
        result={"verified": result.exit_code == 0},
        http_status=200,
    )


def handle_ledger_append(
    ctx: CliContext,
    body: dict[str, Any],
    *,
    repo_arg: str | None = None,
) -> ApiEnvelope:
    allowed = frozenset({"kind", "entry"})
    unknown = _unknown_keys(body, allowed)
    if unknown:
        return bad_request("unknown_fields")

    kind = body.get("kind")
    entry = body.get("entry")
    if not isinstance(kind, str) or kind not in ENTRY_KINDS:
        return bad_request("kind_required")
    if not isinstance(entry, dict):
        return bad_request("entry_required")

    repo_root = resolve_app_repo(ctx.cwd, repo_arg)
    if not (repo_root / ".overseer").is_dir():
        return engine_failure(exit_code=2, error="config", result=None)

    config, config_refusal = load_repo_config(repo_root)
    if config_refusal is not None or config is None:
        return config_refusal or engine_failure(exit_code=2, error="config", result=None)

    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind=kind, body=entry),
    )
    return ApiEnvelope(
        ok=result.exit_code == 0,
        exit_code=result.exit_code,
        error=_ledger_error_token(result.exit_code),
        result={"appended": result.exit_code == 0},
        http_status=200,
    )


def _ledger_error_token(exit_code: int) -> str | None:
    mapping = {
        0: None,
        1: "usage",
        2: "invalid",
        4: "refused",
        5: "write_failed",
        21: "approval_integrity",
        22: "chain_broken",
        23: "role_violation",
        24: "evidence_free",
        25: "provenance",
        26: "signature_required",
    }
    return mapping.get(exit_code, "ledger")


def handle_honesty_status(
    ctx: CliContext,
    body: dict[str, Any],
    *,
    repo_arg: str | None = None,
) -> ApiEnvelope:
    allowed = frozenset(
        {
            "hook",
            "artifact",
            "producer_session",
            "verification_evidence",
            "frozen_spec",
        }
    )
    unknown = _unknown_keys(body, allowed)
    if unknown:
        return bad_request("unknown_fields")

    repo_root = resolve_app_repo(ctx.cwd, repo_arg)
    if not (repo_root / ".overseer").is_dir():
        return engine_failure(exit_code=2, error="config", result=None)

    config, config_refusal = load_repo_config(repo_root)
    if config_refusal is not None or config is None:
        return config_refusal or engine_failure(exit_code=2, error="config", result=None)

    options = HonestyStatusOptions(
        hook=body.get("hook"),
        artifact=body.get("artifact"),
        producer_session=body.get("producer_session"),
        verification_evidence=body.get("verification_evidence"),
        frozen_spec=body.get("frozen_spec"),
        emit_json=True,
    )
    result = run_honesty_status(config=config, repo_root=repo_root, options=options)
    return ApiEnvelope(
        ok=result.exit_code == 0,
        exit_code=result.exit_code,
        error=_honesty_error_token(result.exit_code),
        result=result.json_payload.to_dict(),
        http_status=200,
    )


def _honesty_error_token(exit_code: int) -> str | None:
    mapping = {
        0: None,
        1: "usage",
        4: "refused",
        20: "missing_verdict",
        25: "provenance",
        26: "signature_required",
        33: "missing_verification_evidence",
    }
    return mapping.get(exit_code, "honesty")

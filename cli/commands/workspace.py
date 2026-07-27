"""``ok workspace`` commands (§MR.7)."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.workspace import (
    EXIT_WORKSPACE_RELAY,
    WorkspaceLoadError,
    build_status_report,
    check_next,
    load_manifest_for_repo,
    run_doctor,
)
from tools.workspace.types import EXIT_CONFIG, EXIT_OK, EXIT_USAGE


def run_workspace(args: Namespace, ctx: CliContext) -> int:
    """Dispatch ``ok workspace status|check-next|doctor``."""
    action = getattr(args, "workspace_action", None)
    if action is None:
        ctx.output.error("usage: ok workspace status|check-next|doctor")
        return EXIT_USAGE

    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="workspace")
    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return EXIT_CONFIG

    if action == "status":
        return _run_status(args, ctx, config, repo_root)
    if action == "check-next":
        return _run_check_next(args, ctx, config, repo_root)
    if action == "doctor":
        return _run_doctor(args, ctx, config, repo_root)

    ctx.output.error(f"unknown workspace action: {action}")
    return EXIT_USAGE


def _run_status(args: Namespace, ctx: CliContext, config, repo_root: Path) -> int:
    report = build_status_report(
        config,
        repo_root,
        strict_all=bool(getattr(args, "strict_all", False)),
    )
    if ctx.output.json_mode:
        payload = report.to_json()
        payload["workspace"] = payload  # convenience alias for status --workspace compose
        ctx.output.emit_json(report.to_json())
    else:
        if not report.configured:
            ctx.output.emit("workspace: not_configured")
            return EXIT_OK
        ctx.output.emit(f"workspace.ok: {str(report.ok).lower()}")
        ctx.output.emit(f"workspace.state: {report.state}")
        ctx.output.emit(f"constellation_id: {report.constellation_id}")
        ctx.output.emit(f"product_order_member: {report.product_order_member}")
        ctx.output.emit(f"manifest_source: {report.manifest_source}")
        if report.authoritative_handover:
            ctx.output.emit(f"authoritative_handover: {report.authoritative_handover}")
        for member in report.members:
            base = member.get("handover_basename") or "?"
            ctx.output.emit(
                f"member {member['id']}: role={member['role']} "
                f"status={member['member_status']} handover={base}"
            )
        for warning in report.warnings:
            ctx.output.emit(f"warning: {warning}")
        if report.check_next and report.check_next.get("messages"):
            for msg in report.check_next["messages"]:
                ctx.output.emit(msg)
    # status itself exits 0 even when workspace.ok is false (§MR.12.1 / S9 separation);
    # --exit-code is only on `ok status --workspace --exit-code`.
    return EXIT_OK


def _run_check_next(args: Namespace, ctx: CliContext, config, repo_root: Path) -> int:
    if config.workspace is None:
        payload = {"ok": False, "state": "not_configured", "exit_code": EXIT_CONFIG}
        if ctx.output.json_mode:
            ctx.output.emit_json(payload)
        else:
            ctx.output.error("workspace not configured (check-next requires workspace:)")
        return EXIT_CONFIG
    try:
        manifest = load_manifest_for_repo(config, repo_root)
    except WorkspaceLoadError as exc:
        if ctx.output.json_mode:
            ctx.output.emit_json({"ok": False, "state": "error", "error": str(exc), "exit_code": EXIT_CONFIG})
        else:
            ctx.output.error(str(exc))
        return EXIT_CONFIG

    result = check_next(manifest, lane=getattr(args, "lane", None))
    if ctx.output.json_mode:
        ctx.output.emit_json(
            {
                "ok": result.ok,
                "state": result.state,
                "exit_code": result.exit_code,
                "lane": result.lane,
                "primary": result.primary,
                "relays": list(result.relays),
                "messages": list(result.messages),
            }
        )
    else:
        for msg in result.messages:
            ctx.output.emit(msg)
        if result.ok:
            ctx.output.emit("workspace check-next: ok")
        else:
            ctx.output.error(f"workspace check-next: {result.state}")
    return result.exit_code


def _run_doctor(args: Namespace, ctx: CliContext, config, repo_root: Path) -> int:
    report = run_doctor(config, repo_root)
    if ctx.output.json_mode:
        ctx.output.emit_json(report.to_json())
    else:
        if not report.configured:
            ctx.output.emit("workspace: not_configured")
            return EXIT_OK
        if not report.findings:
            ctx.output.emit("workspace doctor: no findings")
        for finding in report.findings:
            loc = f" [{finding.member_id}]" if finding.member_id else ""
            ctx.output.emit(f"{finding.code}{loc}: {finding.message}")
    return EXIT_OK if report.ok or not report.configured else EXIT_OK

"""``overseer review --freeze`` command (§K5.2)."""

from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path

from adapters.config import load_config
from adapters.errors import ConfigError, ReadError
from adapters.factory import create_adapter
from cli.context import CliContext
from cli.kit_root import kit_version
from cli.paths import PathEscapeError, confine_path, repo_relative, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.freeze_reviewer.checklist import builtin_checklist, load_checklist_file
from tools.freeze_reviewer.engine import ReviewOptions, resolve_exit_code, resolve_reviewer_settings, run_freeze_review
from tools.freeze_reviewer.labels import validate_reviewer_model
from tools.footprint_integrity import check_footprint_integrity
from tools.freeze_reviewer.report import build_report, render_human_report
from tools.muse_sync import check_muse_sync
from tools.substrate_health import check_substrate

DISALLOWED_FLAGS = frozenset(
    {
        "--write-vcs",
        "--commit",
        "--push",
        "--escalate-force-pass",
    }
)


def _validate_raw_argv(argv: list[str]) -> int | None:
    """Reject disallowed flags with USAGE exit 1."""
    for token in argv:
        if token in DISALLOWED_FLAGS:
            return 1
        if token.startswith("--model") and "=" in token:
            value = token.split("=", 1)[1]
            if _looks_like_vendor_slug(value):
                return 1
        if token == "--model":
            return None
    return None


def _looks_like_vendor_slug(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in ("gpt-", "claude-", "composer-"))


def _resolve_effective_checklist(args: Namespace, repo_root: Path) -> tuple[list | None, int | None]:
    if args.checklist is None:
        return builtin_checklist(), None
    try:
        checklist_path = confine_path(repo_root, args.checklist)
    except PathEscapeError:
        return None, 4
    if not checklist_path.is_file():
        return None, 4
    try:
        return load_checklist_file(checklist_path), None
    except ConfigError:
        return None, 2


def _resolve_artifact(args: Namespace, repo_root: Path) -> tuple[Path | None, str | None, int | None]:
    try:
        artifact_path = confine_path(repo_root, args.freeze_path)
    except PathEscapeError:
        return None, None, 4
    if not artifact_path.is_file():
        return None, None, 4
    rel = repo_relative(repo_root, artifact_path)
    return artifact_path, rel, None


def run_review(args: Namespace, ctx: CliContext, *, raw_argv: list[str] | None = None) -> int:
    """Execute ``overseer review --freeze``."""
    argv = raw_argv or []
    disallowed = _validate_raw_argv(argv)
    if disallowed is not None:
        ctx.output.error("usage: invalid or disallowed flag")
        return disallowed

    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="review")
    overseer_dir = repo_root / ".overseer"
    if not overseer_dir.is_dir():
        ctx.output.error("not initialized — run overseer init first")
        return 2

    config_path = resolve_config_path(repo_root, args.config)
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    checklist, checklist_code = _resolve_effective_checklist(args, repo_root)
    if checklist_code is not None:
        if checklist_code == 2:
            ctx.output.error("invalid checklist file")
        else:
            ctx.output.error("refused: checklist path")
        return checklist_code

    artifact_path, rel_path, artifact_code = _resolve_artifact(args, repo_root)
    if artifact_code is not None or artifact_path is None or rel_path is None:
        ctx.output.error("refused: artifact path")
        return artifact_code or 4

    # Validate model label when agent mode effective
    effective_mode = args.mode or config.freeze_contract.reviewer.mode
    effective_model = args.model or config.freeze_contract.reviewer.model
    if effective_mode != "human":
        if args.model and _looks_like_vendor_slug(args.model):
            ctx.output.error("reviewer.model must be a label, not a vendor slug")
            return 1
        try:
            validate_reviewer_model(effective_model, ctx.kit)
        except ConfigError as exc:
            ctx.output.error(format_config_error(exc, repo_root))
            return 2
        if args.provider and args.provider not in {"local", "api"}:
            ctx.output.error("invalid --provider value")
            return 1
        if args.mode and args.mode not in {"agent", "human"}:
            ctx.output.error("invalid --mode value")
            return 1

    adapter = create_adapter(config, repo_root, runner=ctx.runner)
    substrate = check_substrate(config, repo_root)
    if not substrate.ok:
        ctx.output.error(f"substrate: {substrate.state} — {substrate.message}")
        if substrate.remediation:
            ctx.output.error(f"remediation: {substrate.remediation}")
        return 2

    status = adapter.status()
    if isinstance(status, ReadError):
        ctx.output.error(str(status))
        return 2

    muse_sync = check_muse_sync(config, status)
    if not muse_sync.ok:
        ctx.output.error(f"muse_sync: {muse_sync.state} — {muse_sync.message}")
        if muse_sync.remediation:
            ctx.output.error(f"remediation: {muse_sync.remediation}")
        return 2

    footprint_self_integrity = check_footprint_integrity(repo_root)
    if not footprint_self_integrity.ok:
        ctx.output.error(
            f"footprint_self_integrity: {footprint_self_integrity.state} — "
            f"{footprint_self_integrity.message}"
        )
        if footprint_self_integrity.remediation:
            ctx.output.error(f"remediation: {footprint_self_integrity.remediation}")
        return 2

    injected_provider = None
    if ctx.review_provider_factory is not None:
        injected_provider = ctx.review_provider_factory(config.freeze_contract.reviewer.provider)

    options = ReviewOptions(
        dry_run=args.dry_run,
        no_stamp=args.no_stamp,
        mode=args.mode,
        provider=args.provider,
        model=args.model,
        checklist=checklist,
        kit_version=kit_version(),
        kit_root=ctx.kit,
        injected_provider=injected_provider,
    )

    try:
        result = run_freeze_review(
            artifact_path=artifact_path,
            rel_path=rel_path,
            config=config,
            options=options,
        )
    except ValueError as exc:
        if str(exc) == "not-utf8":
            ctx.output.error("refused: artifact not utf-8")
            return 4
        raise

    reviewer = resolve_reviewer_settings(config.freeze_contract, options)
    report = build_report(
        freeze_path=rel_path,
        result=result,
        reviewer=reviewer,
        config=config.freeze_contract,
        enabled=config.freeze_contract.enabled,
    )
    exit_code = resolve_exit_code(
        result,
        config_error=False,
        refused=result.refused,
    )
    report["exit_code"] = exit_code

    if ctx.output.json_mode:
        ctx.output.emit_json(report)
    else:
        ctx.output.emit(render_human_report(freeze_path=rel_path, result=result))

    return exit_code

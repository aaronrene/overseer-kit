"""``overseer verify-step`` command (§K9.5)."""

from __future__ import annotations

import sys
from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.checkpoints.executor import SubprocessScriptExecutor
from tools.checkpoints.orchestrator import VerifyStepOptions, run_verify_step


def _build_options(args: Namespace) -> VerifyStepOptions:
    through_current = False
    if getattr(args, "through", None) == "current":
        through_current = True
    return VerifyStepOptions(
        manifest=args.manifest,
        step_id=args.step,
        through_current=through_current,
        verify_all=bool(args.all),
        policy=args.policy,
        dry_run=bool(args.dry_run),
        emit_json=bool(args.json),
    )


def run_verify_step_command(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer verify-step``."""
    if getattr(args, "through", None) is not None and args.through != "current":
        ctx.output.error("usage: --through accepts only the literal token 'current'")
        if args.json:
            from tools.checkpoints.types import VerifyStepJson

            payload = VerifyStepJson(
                ok=False,
                exit_code=1,
                mode="through",
                dry_run=bool(args.dry_run),
                manifest=args.manifest,
                steps=[],
                error="usage",
            )
            ctx.output.emit_json(payload.to_dict())
        return 1

    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="verify-step")
    overseer_dir = repo_root / ".overseer"
    if not overseer_dir.is_dir():
        ctx.output.error("not initialized — run ok init first")
        if args.json:
            from tools.checkpoints.types import VerifyStepJson

            ctx.output.emit_json(
                VerifyStepJson(
                    ok=False,
                    exit_code=2,
                    dry_run=bool(args.dry_run),
                    steps=[],
                    error="config",
                ).to_dict()
            )
        return 2

    config_path = resolve_config_path(repo_root, args.config)
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        if args.json:
            from tools.checkpoints.types import VerifyStepJson

            ctx.output.emit_json(
                VerifyStepJson(
                    ok=False,
                    exit_code=2,
                    dry_run=bool(args.dry_run),
                    steps=[],
                    error="config",
                ).to_dict()
            )
        return 2

    for warning in config.extension_warnings:
        ctx.output.warn(warning)

    options = _build_options(args)
    executor = ctx.script_executor or SubprocessScriptExecutor()
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=options,
        executor=executor,
    )

    if result.stderr_extra:
        print(result.stderr_extra, file=sys.stderr)

    if options.emit_json:
        ctx.output.emit_json(result.json_payload.to_dict())
    elif result.exit_code == 4 and not config.checkpoints.enabled:
        ctx.output.error("refused: checkpoints.enabled is false")
    elif result.exit_code != 0 and result.json_payload.error == "refused":
        ctx.output.error("refused: path or module gate")
    elif result.exit_code == 10:
        ctx.output.error("verify failed")
    elif result.exit_code == 11:
        ctx.output.error("step order violation")
    elif result.exit_code == 5:
        ctx.output.error("manifest write failed")

    return result.exit_code

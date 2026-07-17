"""``ok pr-land`` — authorized wait-for-green PR merge (Tier-3 delegated)."""

from __future__ import annotations

from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.close_ritual.pr_land import run_pr_land


def run_pr_land_command(args: Namespace, ctx: CliContext) -> int:
    """Execute ``ok pr-land``."""
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="pr-land")
    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        load_config(config_path)  # validate install; pr-land does not need close_ritual.enabled
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    def emit(line: str) -> None:
        if not ctx.output.quiet and not ctx.output.json_mode:
            ctx.output.emit(line)

    result = run_pr_land(
        str(args.pr),
        authorization=str(args.authorized or ""),
        merge_method=str(args.method),
        poll_seconds=float(args.poll_seconds),
        timeout_seconds=float(args.timeout_seconds),
        allow_empty_checks=bool(args.allow_empty_checks),
        dry_run=bool(args.dry_run),
        emit=emit,
        repo_root=repo_root,
    )

    if ctx.output.json_mode:
        ctx.output.emit_json(result.to_dict())
    return result.exit_code

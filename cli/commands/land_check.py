"""``ok land-check`` — close-ritual verify_landed / prepare_pr (never merges)."""

from __future__ import annotations

from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.close_ritual.land_check import run_land_check


def run_land_check_command(args: Namespace, ctx: CliContext) -> int:
    """Execute ``ok land-check``."""
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="land-check")
    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    mode = getattr(args, "mode", None)

    def emit(line: str) -> None:
        if not ctx.output.quiet and not ctx.output.json_mode:
            ctx.output.emit(line)

    result = run_land_check(config, repo_root, mode=mode, emit=emit)

    if ctx.output.json_mode:
        ctx.output.emit_json(
            {
                "exit_code": result.exit_code,
                "landed": result.landed,
                "mode": result.mode,
                "ref": result.ref,
                "paths": list(result.paths),
                "dirty_paths": list(result.dirty_paths),
                "auto_merge": False,
                "messages": list(result.messages),
            }
        )
    return result.exit_code

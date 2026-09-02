"""``ok handover-compact`` command (§LT.6)."""

from __future__ import annotations

import json
from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.handover_compact import compact_handover_change_log


def run_handover_compact_command(args: Namespace, ctx: CliContext) -> int:
    """Archive old handover change-log bullets."""
    if args.write and args.dry_run:
        ctx.output.error("handover-compact: cannot use --write and --dry-run together")
        return 2

    keep = args.keep
    if keep < 5:
        ctx.output.error("handover-compact: --keep must be an integer >= 5")
        return 2

    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="handover-compact")
    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    write = bool(args.write)
    report = compact_handover_change_log(
        config,
        repo_root,
        keep=keep,
        write=write,
        lane=getattr(args, "lane", None),
    )

    if not report.ok:
        ctx.output.error(f"handover-compact: {report.reason}")
        return 2

    if ctx.output.json_mode:
        ctx.output.emit_json(
            {
                "ok": True,
                "compacted": report.compacted,
                "keep": report.keep,
                "archive": report.archive,
                "wrote": report.wrote,
            }
        )
    else:
        ctx.output.emit(
            f"handover-compact: compacted={report.compacted} keep={report.keep} "
            f"archive={report.archive}"
        )

    return 0

"""``overseer ledger`` commands (§K9.9)."""

from __future__ import annotations

import sys
from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import resolve_config_path, resolve_repo_root
from cli.sanitize import config_exit_code, format_config_error
from tools.honesty.ledger import append_entry, parse_append_body, show_entries, verify_ledger_file
from tools.honesty.types import ENTRY_KINDS, LedgerAppendOptions


def run_ledger_command(args: Namespace, ctx: CliContext) -> int:
    """Dispatch ``overseer ledger {append,verify,show}``."""
    action = args.ledger_action
    if action == "append":
        return _run_append(args, ctx)
    if action == "verify":
        return _run_verify(args, ctx)
    if action == "show":
        return _run_show(args, ctx)
    ctx.output.error("usage: ledger requires append|verify|show")
    return 1


def _load_config_or_exit(args: Namespace, ctx: CliContext):
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="ledger")
    overseer_dir = repo_root / ".overseer"
    if not overseer_dir.is_dir():
        ctx.output.error("not initialized — run overseer init first")
        return None, None, 2

    config_path = resolve_config_path(repo_root, args.config)
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return None, None, config_exit_code(exc)

    for warning in config.extension_warnings:
        ctx.output.warn(warning)
    return config, repo_root, None


def _run_append(args: Namespace, ctx: CliContext) -> int:
    if not args.kind:
        ctx.output.error("usage: --kind is required")
        return 1
    if args.file and args.stdin:
        ctx.output.error("usage: at most one of --file or --stdin")
        return 1

    config, repo_root, early = _load_config_or_exit(args, ctx)
    if early is not None:
        return early

    stdin_text = None
    if args.stdin:
        stdin_text = sys.stdin.read()

    body, body_exit, _ = parse_append_body(
        repo_root=repo_root,
        file_path=args.file,
        stdin_text=stdin_text,
    )
    if body_exit != 0:
        if body_exit == 2:
            ctx.output.error("invalid append body")
        else:
            ctx.output.error("refused")
        return body_exit

    if args.kind not in ENTRY_KINDS:
        ctx.output.error("unknown entry kind")
        return 2

    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind=args.kind, body=body or {}),
    )

    if result.stderr_extra:
        for line in result.stderr_extra.splitlines():
            if line.startswith("honesty.roles_file"):
                ctx.output.warn(line)
            else:
                print(line, file=sys.stderr)

    if result.exit_code == 4:
        ctx.output.error("refused")
    elif result.exit_code == 23:
        ctx.output.error("role violation")
    elif result.exit_code == 24:
        ctx.output.error("evidence-free verdict")
    elif result.exit_code == 21:
        ctx.output.error("approval integrity failure")
    elif result.exit_code == 5:
        ctx.output.error("ledger write failed")
    elif result.exit_code == 2:
        ctx.output.error("invalid ledger entry")
    elif result.exit_code == 25:
        ctx.output.error("provenance signature verification failed")
    elif result.exit_code == 26:
        ctx.output.error("signature required but absent")

    return result.exit_code


def _run_verify(args: Namespace, ctx: CliContext) -> int:
    config, repo_root, early = _load_config_or_exit(args, ctx)
    if early is not None:
        return early

    result = verify_ledger_file(config=config, repo_root=repo_root)
    if result.stderr_extra:
        for line in result.stderr_extra.splitlines():
            if line.startswith("honesty.roles_file"):
                ctx.output.warn(line)
            else:
                print(line, file=sys.stderr)

    if result.exit_code == 22:
        ctx.output.error("ledger chain broken")
    elif result.exit_code == 25:
        ctx.output.error("provenance signature verification failed")
    elif result.exit_code == 26:
        ctx.output.error("signature required but absent")
    elif result.exit_code == 2:
        ctx.output.error("malformed provenance envelope")
    elif result.exit_code == 4:
        ctx.output.error("refused")
    return result.exit_code


def _run_show(args: Namespace, ctx: CliContext) -> int:
    last_n = args.last if args.last is not None else 20
    config, repo_root, early = _load_config_or_exit(args, ctx)
    if early is not None:
        return early

    result = show_entries(config=config, repo_root=repo_root, last_n=last_n)
    if result.stderr_extra:
        for line in result.stderr_extra.splitlines():
            if line.startswith("honesty.roles_file"):
                ctx.output.warn(line)
            else:
                print(line, file=sys.stderr)

    if result.exit_code == 1:
        ctx.output.error("usage")
        return 1
    if result.exit_code == 4:
        ctx.output.error("refused")
        return 4
    if result.exit_code == 22:
        ctx.output.error("ledger chain broken")
        return 22

    for line in result.stdout_lines:
        print(line)
    return 0

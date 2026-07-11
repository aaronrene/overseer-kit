"""Overseer CLI entrypoint and argument parsing (§K4.1)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cli.args import extract_global_args

COMMANDS = frozenset({"init", "sync", "status", "review", "governance-sync"})
from cli.commands.governance_sync import run_governance_sync_command
from cli.commands.init import run_init
from cli.commands.review import run_review
from cli.commands.status import run_status
from cli.commands.sync import run_sync
from cli.context import CliContext
from cli.kit_root import kit_version
from cli.output import OutputContext


def build_parser() -> argparse.ArgumentParser:
    """Construct the frozen argument parser."""
    parser = argparse.ArgumentParser(prog="overseer", description="Overseer Kit vendoring CLI")
    parser.add_argument("--version", action="store_true", help="Print kit version and exit")
    parser.add_argument("-C", "--repo", metavar="PATH", help="Repo root")
    parser.add_argument("--config", metavar="PATH", help="Config file path")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential stdout")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose diagnostics on stderr")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color")

    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="First install into a repo")
    init_parser.add_argument("--regime", choices=["muse+git-mirror", "muse-only", "git-only"])
    init_parser.add_argument("--repo-name", metavar="NAME")
    init_parser.add_argument("--docs-dir", metavar="PATH", default="docs")
    init_parser.add_argument("--from-config", metavar="PATH")
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument("--non-interactive", action="store_true")
    init_parser.add_argument("--dry-run", action="store_true")

    sync_parser = subparsers.add_parser("sync", help="Update vendored footprint")
    sync_parser.add_argument("--dry-run", action="store_true")
    sync_parser.add_argument("--diff", action="store_true", default=None)
    sync_parser.add_argument("--no-diff", action="store_false", dest="diff")
    sync_parser.add_argument("--only", action="append", metavar="GLOB")
    sync_parser.add_argument("--force", action="store_true")
    sync_parser.add_argument("-y", "--yes", action="store_true")

    status_parser = subparsers.add_parser("status", help="Read-only status report")
    status_parser.add_argument("--exit-code", action="store_true")
    status_parser.add_argument("--check-footprint", action="store_true")

    review_parser = subparsers.add_parser("review", help="Freeze-contract review")
    review_parser.add_argument("--freeze", required=True, dest="freeze_path", metavar="PATH")
    review_parser.add_argument("--dry-run", action="store_true")
    review_parser.add_argument("--mode", choices=["agent", "human"])
    review_parser.add_argument("--provider", choices=["local", "api"])
    review_parser.add_argument("--model", metavar="LABEL")
    review_parser.add_argument("--no-stamp", action="store_true")
    review_parser.add_argument("--checklist", metavar="PATH")

    gs_parser = subparsers.add_parser(
        "governance-sync",
        help="Governance hygiene agent (default dry-run)",
    )
    gs_parser.add_argument(
        "--write",
        action="store_true",
        help="Apply doc patches, commit on feature branch, and push (default is dry-run)",
    )
    gs_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run (default when --write is absent)",
    )

    return parser


def main(argv: list[str] | None = None, *, ctx: CliContext | None = None) -> int:
    """CLI main; return exit code."""
    parser = build_parser()
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    global_argv, rest_argv = extract_global_args(raw_argv)
    if rest_argv and rest_argv[0] not in COMMANDS:
        print(f"unknown command: {rest_argv[0]}", file=sys.stderr)
        return 1
    try:
        args = parser.parse_args(global_argv + rest_argv)
    except SystemExit as exc:
        code = exc.code
        return 1 if code == 2 else (int(code) if isinstance(code, int) else 1)

    if args.version:
        print(kit_version())
        return 0

    if args.command is None:
        parser.print_help()
        return 0

    runtime = ctx or CliContext.create()
    if ctx is None:
        runtime = CliContext.create(
            output=OutputContext(
                json_mode=args.json,
                quiet=args.quiet,
                verbose=args.verbose,
                no_color=args.no_color,
            ),
            cwd=Path.cwd(),
        )
    else:
        runtime.output.json_mode = args.json or runtime.output.json_mode
        runtime.output.quiet = args.quiet or runtime.output.quiet
        runtime.output.verbose = args.verbose or runtime.output.verbose
        runtime.output.no_color = args.no_color or runtime.output.no_color

    if args.command == "init":
        return run_init(args, runtime)
    if args.command == "sync":
        if args.diff is None:
            args.diff = sys.stdout.isatty()
        return run_sync(args, runtime)
    if args.command == "status":
        return run_status(args, runtime)
    if args.command == "review":
        return run_review(args, runtime, raw_argv=rest_argv)
    if args.command == "governance-sync":
        return run_governance_sync_command(args, runtime)

    parser.error(f"unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

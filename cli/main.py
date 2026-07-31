"""Overseer CLI entrypoint and argument parsing (§K4.1)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cli.args import extract_global_args

COMMANDS = frozenset(
    {
        "init",
        "sync",
        "status",
        "review",
        "check-ok",
        "check-if-ok",  # synonym → check-ok
        "governance-sync",
        "workspace",
        "verify-step",
        "honesty-status",
        "ledger",
        "route",
        "app",
        "hosted-dashboard",
        "upgrade-regime",
        "land-check",
        "land-closeout",
        "pr-land",
    }
)
from cli.commands.app import run_app
from cli.commands.check_ok import run_check_ok
from cli.commands.governance_sync import run_governance_sync_command
from cli.commands.honesty_status import run_honesty_status_command
from cli.commands.hosted_dashboard import run_hosted_dashboard
from cli.commands.init import run_init
from cli.commands.land_check import run_land_check_command
from cli.commands.land_closeout import run_land_closeout_command
from cli.commands.ledger import run_ledger_command
from cli.commands.pr_land import run_pr_land_command
from cli.commands.review import run_review
from cli.commands.status import run_status
from cli.commands.sync import run_sync
from cli.commands.route import run_route_command
from cli.commands.upgrade_regime import run_upgrade_regime_command
from cli.commands.verify_step import run_verify_step_command
from cli.commands.workspace import run_workspace
from cli.context import CliContext
from cli.kit_root import kit_version
from cli.output import OutputContext


def build_parser() -> argparse.ArgumentParser:
    """Construct the frozen argument parser."""
    parser = argparse.ArgumentParser(prog="ok", description="Overseer Kit vendoring CLI")
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
    init_parser.add_argument(
        "--migrate",
        action="store_true",
        help="Preserve existing living docs; lock origin:preserved (K6)",
    )
    init_parser.add_argument(
        "--include-preserved",
        action="store_true",
        help="With --force: promote living docs to origin:kit (pilot-forbidden)",
    )
    init_parser.add_argument(
        "--preserve-shared-assets",
        action="store_true",
        help=(
            "Preserve existing differing shared assets (non-living footprint); "
            "lock origin:preserved. With --force still does not overwrite them "
            "unless --include-preserved"
        ),
    )

    sync_parser = subparsers.add_parser("sync", help="Update vendored footprint")
    sync_parser.add_argument("--dry-run", action="store_true")
    sync_parser.add_argument("--diff", action="store_true", default=None)
    sync_parser.add_argument("--no-diff", action="store_false", dest="diff")
    sync_parser.add_argument("--only", action="append", metavar="GLOB")
    sync_parser.add_argument("--force", action="store_true")
    sync_parser.add_argument("-y", "--yes", action="store_true")
    sync_parser.add_argument(
        "--include-preserved",
        action="store_true",
        help="With --force: promote living docs to origin:kit (pilot-forbidden)",
    )

    status_parser = subparsers.add_parser("status", help="Read-only status report")
    status_parser.add_argument("--exit-code", action="store_true")
    status_parser.add_argument("--check-footprint", action="store_true")
    status_parser.add_argument(
        "--workspace",
        action="store_true",
        help="Attach constellation workspace report when configured (§MR.7)",
    )

    review_parser = subparsers.add_parser("review", help="Freeze-contract review")
    review_parser.add_argument("--freeze", required=True, dest="freeze_path", metavar="PATH")
    review_parser.add_argument("--dry-run", action="store_true")
    review_parser.add_argument("--mode", choices=["agent", "human"])
    review_parser.add_argument("--provider", choices=["local", "api"])
    review_parser.add_argument("--model", metavar="LABEL")
    review_parser.add_argument("--no-stamp", action="store_true")
    review_parser.add_argument("--checklist", metavar="PATH")

    def _add_check_ok_flags(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--path",
            metavar="PATH",
            help="Existing or new freeze artifact (default: docs/reviews/<date>-<topic>.md)",
        )
        parser.add_argument(
            "--topic",
            metavar="SLUG",
            help="Topic label used when scaffolding a new side-check doc",
        )
        parser.add_argument(
            "--scope",
            metavar="TEXT",
            help="Optional scope paragraph written into a new scaffold",
        )
        parser.add_argument(
            "--scaffold-only",
            action="store_true",
            help="Create/reuse the artifact only; do not run freeze review",
        )
        parser.add_argument(
            "--force-scaffold",
            action="store_true",
            help="Overwrite an existing side-check file when scaffolding",
        )
        parser.add_argument("--dry-run", action="store_true", help="Passed through to review --freeze")
        parser.add_argument("--mode", choices=["agent", "human"])
        parser.add_argument("--provider", choices=["local", "api"])
        parser.add_argument("--model", metavar="LABEL")
        parser.add_argument("--no-stamp", action="store_true")
        parser.add_argument("--checklist", metavar="PATH")

    cio_parser = subparsers.add_parser(
        "check-ok",
        help="Check OK: ad-hoc honesty check (scaffold + review --freeze)",
    )
    _add_check_ok_flags(cio_parser)
    cio_alias = subparsers.add_parser(
        "check-if-ok",
        help="Synonym for check-ok (deprecated name)",
    )
    _add_check_ok_flags(cio_alias)

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
    gs_parser.add_argument(
        "--lane",
        metavar="NAME",
        help="Sync only this configured docs lane (requires docs.lanes in config)",
    )
    gs_parser.add_argument(
        "--all-lanes",
        action="store_true",
        help="Sync every configured lane; skip lanes with missing doc files",
    )

    ws_parser = subparsers.add_parser(
        "workspace",
        help="Multi-repo constellation status / relay freshness (§MR.7)",
    )
    ws_sub = ws_parser.add_subparsers(dest="workspace_action", required=True)
    ws_status = ws_sub.add_parser("status", help="Constellation map + relay freshness")
    ws_status.add_argument(
        "--strict-all",
        action="store_true",
        help="Treat optional member absences as failures",
    )
    ws_check = ws_sub.add_parser(
        "check-next",
        help="Fail closed on stale/ambiguous/missing relay tips (exit 35)",
    )
    ws_check.add_argument(
        "--lane",
        metavar="ID",
        help="Constellation lane id (default: primary/product lane)",
    )
    ws_sub.add_parser("doctor", help="Diagnostics including board_name_violation")

    lc_parser = subparsers.add_parser(
        "land-check",
        help="Close-ritual land-to-main check (never auto-merges)",
    )
    lc_parser.add_argument(
        "--mode",
        choices=("verify_landed", "prepare_pr"),
        help="Override close_ritual.mode from config",
    )

    lco_parser = subparsers.add_parser(
        "land-closeout",
        help="Post-merge land closeout probe (§PMHF; never merges, never writes docs)",
    )
    lco_parser.add_argument(
        "--probe-merged-pr",
        action="store_true",
        dest="probe_merged_pr",
        default=None,
        help="Force gh merged-PR enrichment on (default: on for git regimes)",
    )
    lco_parser.add_argument(
        "--no-probe-merged-pr",
        action="store_false",
        dest="probe_merged_pr",
        help="Disable gh merged-PR enrichment",
    )

    pl_parser = subparsers.add_parser(
        "pr-land",
        help="Authorized wait-for-green PR merge (Tier-3 delegated; requires --authorized)",
    )
    pl_parser.add_argument("--pr", required=True, help="PR number or URL")
    pl_parser.add_argument(
        "--authorized",
        default="",
        help='Operator authorization reason (required). Example: "Aaron: land after green"',
    )
    pl_parser.add_argument(
        "--method",
        choices=("squash", "merge", "rebase"),
        default="squash",
        help="Merge method (default: squash)",
    )
    pl_parser.add_argument("--poll-seconds", type=float, default=20.0)
    pl_parser.add_argument("--timeout-seconds", type=float, default=1800.0)
    pl_parser.add_argument(
        "--allow-empty-checks",
        action="store_true",
        help="Treat zero reported checks as pass",
    )
    pl_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Wait/verify only; do not merge",
    )

    vs_parser = subparsers.add_parser("verify-step", help="L1 checkpoint orchestrator (K9b)")
    vs_parser.add_argument("--manifest", metavar="PATH", help="Active manifest path")
    vs_parser.add_argument("--step", metavar="ID", help="Verify one step")
    vs_parser.add_argument(
        "--through",
        metavar="TOKEN",
        help="Verify through current step (only 'current' accepted)",
    )
    vs_parser.add_argument("--all", action="store_true", help="Verify full template order")
    vs_parser.add_argument("--policy", metavar="PATH", help="Policy file override")
    vs_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan only; no script invoke or manifest writes",
    )

    hs_parser = subparsers.add_parser("honesty-status", help="L2 co-requirement check (K10)")
    hs_parser.add_argument("--hook", metavar="HOOK")
    hs_parser.add_argument("--artifact", metavar="PATH")
    hs_parser.add_argument("--producer-session", metavar="ID")
    hs_parser.add_argument("--verification-evidence", metavar="PHASE_ID")
    hs_parser.add_argument("--frozen-spec", metavar="PATH_STRING")
    hs_parser.add_argument("--deploy-health", metavar="PHASE_ID")

    ledger_parser = subparsers.add_parser("ledger", help="L2 verdict ledger (K10)")
    ledger_sub = ledger_parser.add_subparsers(dest="ledger_action", required=True)

    append_parser = ledger_sub.add_parser("append", help="Append a ledger entry")
    append_parser.add_argument("--kind", metavar="KIND", required=True)
    append_parser.add_argument("--file", metavar="JSON_PATH")
    append_parser.add_argument("--stdin", action="store_true")

    ledger_sub.add_parser("verify", help="Verify ledger hash chain")

    show_parser = ledger_sub.add_parser("show", help="Show recent ledger entries")
    show_parser.add_argument("--last", type=int, metavar="N")

    route_parser = subparsers.add_parser("route", help="Read-only model-routing resolution (§PR.6)")
    route_parser.add_argument("--position", metavar="STR")
    route_parser.add_argument("--phase-tier", metavar="ID", dest="phase_tier")
    route_parser.add_argument("--gate", metavar="ID")
    route_parser.add_argument("--validate", action="store_true")

    app_parser = subparsers.add_parser("app", help="Local loopback web UI (Track Q)")
    app_parser.add_argument("--port", type=int, default=8765, metavar="PORT")
    app_parser.add_argument("--bind", default="127.0.0.1", metavar="ADDRESS")
    app_parser.add_argument("--open", action="store_true", help="Open default browser after listen")

    hd_parser = subparsers.add_parser(
        "hosted-dashboard",
        help="Read-only remote governance dashboard preview (§HGD)",
    )
    hd_parser.add_argument("--port", type=int, default=8766, metavar="PORT")
    hd_parser.add_argument("--bind", default="127.0.0.1", metavar="ADDRESS")
    hd_parser.add_argument("--config", metavar="PATH", help="Config file with hosted_dashboard block")
    hd_parser.add_argument("--open", action="store_true", help="Open default browser after listen")

    ur_parser = subparsers.add_parser(
        "upgrade-regime",
        help="Stage 3 ceremony: muse-only → muse+git-mirror (Track O / O3)",
    )
    ur_parser.add_argument(
        "--from",
        dest="from_regime",
        required=True,
        choices=["muse-only"],
        help="Start regime (only muse-only supported in O3)",
    )
    ur_parser.add_argument(
        "--to",
        dest="to_regime",
        required=True,
        choices=["muse+git-mirror"],
        help="Target regime (only muse+git-mirror supported in O3)",
    )
    ur_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan C0–C5 + G1–G8 report; no writes (default when --apply absent)",
    )
    ur_parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform C2–C4 writes and C5 gates; no C7 unless --live-bridge",
    )
    ur_parser.add_argument(
        "--live-bridge",
        action="store_true",
        help="After apply + G1–G8, run C7 via scripts/muse-bridge-deploy.sh (requires -y)",
    )
    ur_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite conflicting kit-owned bridge assets only (never include-preserved)",
    )
    ur_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="C6 consent for --live-bridge after gates pass (refuse --yes alone without gates)",
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
    if args.command in {"check-ok", "check-if-ok"}:
        return run_check_ok(args, runtime, raw_argv=rest_argv)
    if args.command == "governance-sync":
        return run_governance_sync_command(args, runtime)
    if args.command == "workspace":
        return run_workspace(args, runtime)
    if args.command == "land-check":
        return run_land_check_command(args, runtime)
    if args.command == "land-closeout":
        return run_land_closeout_command(args, runtime)
    if args.command == "pr-land":
        return run_pr_land_command(args, runtime)
    if args.command == "verify-step":
        return run_verify_step_command(args, runtime)
    if args.command == "honesty-status":
        return run_honesty_status_command(args, runtime)
    if args.command == "ledger":
        return run_ledger_command(args, runtime)
    if args.command == "route":
        return run_route_command(args, runtime)
    if args.command == "app":
        return run_app(args, runtime)
    if args.command == "hosted-dashboard":
        return run_hosted_dashboard(args, runtime)
    if args.command == "upgrade-regime":
        return run_upgrade_regime_command(args, runtime)

    parser.error(f"unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

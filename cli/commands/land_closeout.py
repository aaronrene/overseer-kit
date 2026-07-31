"""``ok land-closeout`` — post-merge closeout probe (§PMHF.6.3; never merges/writes)."""

from __future__ import annotations

from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.land_closeout import check_land_closeout, land_closeout_payload


def run_land_closeout_command(args: Namespace, ctx: CliContext) -> int:
    """Execute ``ok land-closeout``; exit 0 when ``report.ok`` else 2."""
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="land-closeout")
    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    probe = getattr(args, "probe_merged_pr", None)
    if probe is None:
        # §PMHF.5.3 default: probe when the regime has git/gh; never for muse-only.
        probe = config.vcs.regime != "muse-only"

    report = check_land_closeout(
        config,
        repo_root,
        runner=ctx.runner,
        probe_merged_pr=probe,
    )

    exit_code = 0 if report.ok else 2
    if ctx.output.json_mode:
        payload = land_closeout_payload(report)
        payload["exit_code"] = exit_code
        ctx.output.emit_json(payload)
    else:
        ctx.output.emit(f"land_closeout: {report.state} — {report.message}")
        if report.remediation:
            ctx.output.emit(f"land_closeout-remediation: {report.remediation}")
    return exit_code

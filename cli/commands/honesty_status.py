"""``overseer honesty-status`` command (§K9.8 / §K9.9)."""

from __future__ import annotations

import sys
from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import resolve_config_path, resolve_repo_root
from cli.sanitize import config_exit_code, format_config_error
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import HonestyStatusJson


def run_honesty_status_command(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer honesty-status``."""
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="honesty-status")
    overseer_dir = repo_root / ".overseer"
    if not overseer_dir.is_dir():
        ctx.output.error("not initialized — run ok init first")
        if args.json:
            ctx.output.emit_json(
                HonestyStatusJson(
                    ok=False,
                    exit_code=2,
                    hook=getattr(args, "hook", None),
                    artifact=getattr(args, "artifact", None),
                    producer_session=getattr(args, "producer_session", None),
                    error="config",
                ).to_dict()
            )
        return 2

    config_path = resolve_config_path(repo_root, args.config)
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        exit_code = config_exit_code(exc)
        ctx.output.error(format_config_error(exc, repo_root))
        if args.json:
            ctx.output.emit_json(
                HonestyStatusJson(
                    ok=False,
                    exit_code=exit_code,
                    hook=getattr(args, "hook", None),
                    artifact=getattr(args, "artifact", None),
                    producer_session=getattr(args, "producer_session", None),
                    error="config",
                ).to_dict()
            )
        return exit_code

    for warning in config.extension_warnings:
        ctx.output.warn(warning)

    options = HonestyStatusOptions(
        hook=args.hook,
        artifact=args.artifact,
        producer_session=args.producer_session,
        verification_evidence=getattr(args, "verification_evidence", None),
        frozen_spec=getattr(args, "frozen_spec", None),
        deploy_health=getattr(args, "deploy_health", None),
        independent_second_review=getattr(args, "independent_second_review", None),
        emit_json=bool(args.json),
    )
    result = run_honesty_status(config=config, repo_root=repo_root, options=options)

    if result.stderr_extra:
        for line in result.stderr_extra.splitlines():
            if line.startswith("warning:"):
                ctx.output.warn(line)
            else:
                print(line, file=sys.stderr)

    if options.emit_json:
        ctx.output.emit_json(result.json_payload.to_dict())
    elif result.exit_code == 4:
        ctx.output.error("refused")
    elif result.exit_code == 20:
        ctx.output.error("missing independent verdict")
    elif result.exit_code == 25:
        ctx.output.error("provenance signature verification failed")
    elif result.exit_code == 26:
        ctx.output.error("signature required but absent")
    elif result.exit_code == 33:
        ctx.output.error("missing verification evidence")
    elif result.exit_code == 34:
        ctx.output.error("missing deploy health")
    elif result.exit_code == 38:
        ctx.output.error("missing independent second review")
    elif result.exit_code == 1:
        ctx.output.error("usage")

    return result.exit_code

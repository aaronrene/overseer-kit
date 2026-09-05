"""``ok next`` — print the paste-ready NEXT fence from disk (§ONS.5 / §NXP)."""

from __future__ import annotations

from argparse import Namespace

from adapters.config import load_config, resolve_lane_docs
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.docs_paths import join_docs_rel, living_doc_abs
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.print_next.extract import (
    CURRENT_NEXT_HEADING,
    REASON_REPO_ROOT_UNRESOLVED,
    CurrentNextError,
    CurrentNextResult,
    absolute_repo_root,
    extract_current_next,
    format_current_next,
    read_at_now,
)

EXIT_NEXT_MALFORMED = 37
EXIT_CONFIG = 2


def _reject_lane_name(lane: str | None) -> str | None:
    """Return an error detail when ``lane`` is not a safe identifier (§ONS.11)."""
    if lane is None:
        return None
    if any(token in lane for token in ("/", "\\")) or ".." in lane:
        return f"invalid lane name {lane!r} (identifiers only; no path segments)"
    return None


def _resolved_lane_label(config, lane_arg: str | None) -> str | None:
    """JSON ``lane``: null when docs.lanes unset; else resolved name (§ONS.5.5)."""
    if config.docs.lanes is None:
        return None
    return (lane_arg or config.docs.default_lane or "").strip() or None


def _repo_name_or_none(config) -> str | None:
    name = (config.repo.name or "").strip()
    return name or None


def run_next_command(args: Namespace, ctx: CliContext) -> int:
    """Print the CURRENT NEXT paste fence (read-only; no Muse/git)."""
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="next")
    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    lane_arg = getattr(args, "lane", None)
    bad_lane = _reject_lane_name(lane_arg)
    if bad_lane is not None:
        ctx.output.error(f"next: config — {bad_lane}")
        return EXIT_CONFIG

    repo_root_abs = absolute_repo_root(repo_root)
    read_at = read_at_now()

    if repo_root_abs is None:
        err = CurrentNextError(
            reason=REASON_REPO_ROOT_UNRESOLVED,
            detail="cannot resolve repo root for provenance",
        )
        return _emit_error(
            ctx,
            err,
            repo_name=None,
            repo_root=None,
            read_at=read_at,
            exit_code=EXIT_CONFIG,
        )

    try:
        config = load_config(config_path)
        lane_docs = resolve_lane_docs(config, lane_arg)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return EXIT_CONFIG

    rel_path = join_docs_rel(config.repo.root_relative_docs, lane_docs.handover)
    handover_path = living_doc_abs(repo_root, config, lane_docs.handover)
    if not is_within_repo(repo_root, handover_path):
        ctx.output.error("refused: handover path outside repo root")
        return 4

    lane_label = _resolved_lane_label(config, lane_arg)
    repo_name = _repo_name_or_none(config)
    # Capture read_at at disk-read time (§NXP.3.2).
    read_at = read_at_now()
    outcome = extract_current_next(
        handover_path,
        repo_relative_path=rel_path,
        lane=lane_label,
    )

    if isinstance(outcome, CurrentNextError):
        return _emit_error(
            ctx,
            outcome,
            repo_name=repo_name,
            repo_root=repo_root_abs,
            read_at=read_at,
        )

    return _emit_success(
        ctx,
        outcome,
        repo_name=repo_name,
        repo_root=repo_root_abs,
        read_at=read_at,
    )


def _emit_success(
    ctx: CliContext,
    result: CurrentNextResult,
    *,
    repo_name: str | None,
    repo_root: str,
    read_at: str,
) -> int:
    if ctx.output.json_mode:
        ctx.output.emit_json(
            {
                "ok": True,
                "path": result.path,
                "lane": result.lane,
                "heading": CURRENT_NEXT_HEADING,
                "fence": result.fence,
                "error": None,
                "repo_name": repo_name,
                "repo_root": repo_root,
                "read_at": read_at,
            }
        )
        return 0

    # Product block — print even under --quiet (§ONS.5.4 / §NXP.3.5).
    print(
        format_current_next(
            result,
            repo_name=repo_name,
            repo_root_abs=repo_root,
            read_at=read_at,
        ),
        end="",
    )
    return 0


def _emit_error(
    ctx: CliContext,
    err: CurrentNextError,
    *,
    repo_name: str | None,
    repo_root: str | None,
    read_at: str,
    exit_code: int = EXIT_NEXT_MALFORMED,
) -> int:
    if ctx.output.json_mode:
        ctx.output.emit_json(
            {
                "ok": False,
                "path": err.path,
                "lane": err.lane,
                "heading": CURRENT_NEXT_HEADING,
                "fence": None,
                "error": err.reason,
                "message": err.message,
                "repo_name": repo_name,
                "repo_root": repo_root,
                "read_at": read_at,
            }
        )
    else:
        ctx.output.error(err.message)
    return exit_code

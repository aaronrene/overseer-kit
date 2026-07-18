"""``ok check-ok`` — scaffold (optional) + same ``review --freeze`` engine.

``check-if-ok`` remains a CLI synonym for one release.
"""

from __future__ import annotations

from argparse import Namespace

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.commands.review import run_review
from cli.context import CliContext
from cli.paths import PathEscapeError, confine_path, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.check_ok.scaffold import scaffold_side_check


def run_check_ok(args: Namespace, ctx: CliContext, *, raw_argv: list[str] | None = None) -> int:
    """Scaffold a side-check artifact when needed, then run freeze review.

    Semantic review / build-verification loops stay in portable skills
    (``/check-ok``, ``/freeze-review-loop``, ``/build-verification-review``) under
    ``.cursor/skills/`` and ``.claude/skills/``. This CLI path is the tool-agnostic
    mechanical gate — identical engine to ``ok review --freeze``.
    """
    del raw_argv  # reserved for parity with review; no extra flag bans yet
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="check-ok")
    overseer_dir = repo_root / ".overseer"
    if not overseer_dir.is_dir():
        ctx.output.error("not initialized — run ok init first")
        return 2

    config_path = resolve_config_path(repo_root, args.config)
    try:
        load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    path_arg = args.path
    if path_arg:
        try:
            confined = confine_path(repo_root, path_arg)
            path_arg = confined.relative_to(repo_root.resolve()).as_posix()
        except (PathEscapeError, ValueError):
            ctx.output.error("refused: artifact path")
            return 4

    try:
        result = scaffold_side_check(
            repo_root,
            path=path_arg,
            topic=args.topic,
            scope=args.scope or "",
            overwrite=bool(args.force_scaffold),
        )
    except ValueError as exc:
        if str(exc) == "path-escape":
            ctx.output.error("refused: artifact path")
            return 4
        raise

    if result.created:
        ctx.output.emit(f"check-ok: scaffolded {result.rel_path}")
    else:
        ctx.output.emit(f"check-ok: reusing {result.rel_path}")

    if args.scaffold_only:
        if ctx.output.json_mode:
            ctx.output.emit_json(
                {
                    "command": "check-ok",
                    "rel_path": result.rel_path,
                    "created": result.created,
                    "scaffold_only": True,
                    "exit_code": 0,
                }
            )
        return 0

    review_args = Namespace(
        repo=args.repo,
        config=args.config,
        freeze_path=result.rel_path,
        dry_run=bool(args.dry_run),
        no_stamp=bool(args.no_stamp),
        mode=args.mode,
        provider=args.provider,
        model=args.model,
        checklist=args.checklist,
    )
    return run_review(review_args, ctx, raw_argv=["review", "--freeze", result.rel_path])


# Back-compat import name used by older call sites / docs mid-rename.
run_check_if_ok = run_check_ok

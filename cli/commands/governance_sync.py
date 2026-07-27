"""``overseer governance-sync`` command (§9A-5)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from adapters.errors import ConfigError
from adapters.factory import create_adapter
from cli.context import CliContext
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error
from tools.governance_hygiene.engine import run_governance_sync


def run_governance_sync_command(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer governance-sync`` (default: dry-run)."""
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="governance-sync")
    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    adapter = create_adapter(config, repo_root, runner=ctx.runner)
    dry_run = not args.write
    messages: list[str] = []

    def emit(line: str) -> None:
        messages.append(line)
        if not ctx.output.quiet:
            if ctx.output.json_mode:
                return
            ctx.output.emit(line)

    result = run_governance_sync(
        config,
        repo_root,
        adapter,
        ctx.runner,
        dry_run=dry_run,
        lane=getattr(args, "lane", None),
        all_lanes=getattr(args, "all_lanes", False),
        emit=emit,
        kit_root=ctx.kit,
    )

    if ctx.output.json_mode:
        payload = {
            "dry_run": result.dry_run,
            "exit_code": result.exit_code,
            "committed": result.committed,
            "commit_sha": result.commit_sha,
            "error_command": result.error_command,
            "messages": list(result.messages) + messages,
            "workspace_relay": result.workspace_relay,
        }
        if result.drift is not None:
            payload["drift"] = {
                "d1": result.drift.d1_handover_vs_git,
                "d2": result.drift.d2_anchor_vs_canonical,
                "d3": result.drift.d3_queue_vs_merged,
                "details": result.drift.details,
            }
        if result.reads is not None:
            payload["reads"] = {
                "regime": result.reads.regime,
                "r1_github_main_sha": result.reads.r1_github_main_sha,
                "r2_anchor_sha": result.reads.r2_anchor_sha,
                "r3_canonical_main_sha": result.reads.r3_canonical_main_sha,
                "r5_branch": result.reads.r5_branch,
                "r5_dirty": result.reads.r5_dirty,
                "merged_pr_count": len(result.reads.r4_merged_prs),
            }
        if result.plan is not None:
            payload["plan"] = {
                "patched_sections": list(result.plan.patched_sections),
                "feature_branch": result.plan.feature_branch,
                "realign_planned": result.plan.realign_planned,
                "pr_url": result.plan.pr_url,
            }
        ctx.output.emit_json(payload)

    return result.exit_code

"""``overseer route`` command (§PR.6)."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from adapters.config import OverseerConfig, load_config
from adapters.errors import ConfigError
from cli.context import CliContext
from cli.paths import PathEscapeError, confine_path, is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import config_exit_code, format_config_error
from tools.cost_awareness.derive import derive_cost_view
from tools.model_routing.labels import RoutingPolicyError, load_model_tier_cost_bands
from tools.model_routing.policy import load_routing_policy, validate_routing_policy
from tools.model_routing.resolve import resolve_route
from tools.model_routing.types import RouteSelector


def _resolve_policy_path(config: OverseerConfig, repo_root: Path) -> Path:
    """Resolve configured policy path confined to repo root."""
    return confine_path(repo_root, config.model_routing.policy)


def run_route_command(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer route`` (read-only; no model call, no network)."""
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="route")
    overseer_dir = repo_root / ".overseer"
    if not overseer_dir.is_dir():
        ctx.output.error("not initialized — run overseer init first")
        return 1

    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return config_exit_code(exc)

    for warning in config.extension_warnings:
        ctx.output.warn(warning)

    try:
        policy_path = _resolve_policy_path(config, repo_root)
    except PathEscapeError:
        ctx.output.error("refused: model_routing.policy path outside repo root")
        return 4

    if args.validate:
        return _run_validate(config=config, policy_path=policy_path, kit_root=ctx.kit, ctx=ctx)

    query = RouteSelector(
        position=args.position,
        phase_tier=args.phase_tier,
        gate=args.gate,
    )
    return _run_resolve(
        config=config,
        policy_path=policy_path,
        kit_root=ctx.kit,
        query=query,
        ctx=ctx,
    )


def _run_validate(
    *,
    config: OverseerConfig,
    policy_path: Path,
    kit_root: Path,
    ctx: CliContext,
) -> int:
    result = validate_routing_policy(policy_path, kit_root=kit_root)
    payload = {
        "valid": result.valid,
        "policy": config.model_routing.policy,
        "violation": result.violation,
    }
    if ctx.output.json_mode:
        ctx.output.emit_json(payload)
    elif result.valid:
        ctx.output.emit("routing policy: valid")
    else:
        ctx.output.error(result.violation or "routing policy invalid")
    if result.valid:
        return 0
    if result.violation and "missing or unreadable" in result.violation:
        return 31
    return 30


def _run_resolve(
    *,
    config: OverseerConfig,
    policy_path: Path,
    kit_root: Path,
    query: RouteSelector,
    ctx: CliContext,
) -> int:
    try:
        policy = load_routing_policy(policy_path, kit_root=kit_root)
    except RoutingPolicyError as exc:
        ctx.output.error(exc.message)
        return exc.exit_code

    try:
        cost_bands = load_model_tier_cost_bands(kit_root, fail_closed=True)
    except RoutingPolicyError as exc:
        ctx.output.error(exc.message)
        return exc.exit_code

    decision = resolve_route(policy, query)
    cost_class, paid_step_before_spend = derive_cost_view(decision.model_tier, cost_bands)
    payload = {
        "route_id": decision.route_id,
        "model_tier": decision.model_tier,
        "fallback": list(decision.fallback),
        "query": {
            "position": query.position,
            "phase_tier": query.phase_tier,
            "gate": query.gate,
        },
        "policy": config.model_routing.policy,
        "cost_class": cost_class,
        "paid_step_before_spend": paid_step_before_spend,
    }
    if ctx.output.json_mode:
        ctx.output.emit_json(payload)
    else:
        ctx.output.emit(f"route_id: {decision.route_id}")
        ctx.output.emit(f"model_tier: {decision.model_tier}")
        ctx.output.emit(f"fallback: {', '.join(decision.fallback)}")
        ctx.output.emit(f"cost_class: {cost_class}")
        ctx.output.emit(f"paid_step_before_spend: {paid_step_before_spend}")
    return 0


def routing_policy_status(config: OverseerConfig, repo_root: Path, *, kit_root: Path) -> dict:
    """Read-only routing-policy validity for ``overseer status`` when enabled."""
    if not config.model_routing.enabled:
        return {"enabled": False}
    try:
        policy_path = _resolve_policy_path(config, repo_root)
    except PathEscapeError:
        return {
            "enabled": True,
            "policy": config.model_routing.policy,
            "valid": False,
            "violation": "model_routing.policy path escapes repo root",
        }
    result = validate_routing_policy(policy_path, kit_root=kit_root)
    return {
        "enabled": True,
        "policy": config.model_routing.policy,
        "valid": result.valid,
        "violation": result.violation,
    }

"""Data-integrity tests for Track P / P-route (§PR.8)."""

from __future__ import annotations

from cli.footprint import resolve_footprint
from cli.kit_root import kit_root
from tests.fixtures.model_routing import seed_routing_repo
from tests.support import git_status_runner, run_cli
from tools.model_routing.policy import validate_routing_policy
from tools.model_routing.resolve import resolve_route
from tools.model_routing.types import RouteSelector


def test_resolution_idempotent(tmp_path) -> None:
    policy_path = seed_routing_repo(tmp_path)
    from tools.model_routing.policy import load_routing_policy

    policy = load_routing_policy(policy_path, kit_root=kit_root())
    query = RouteSelector(gate="freeze_review", phase_tier="thinking")
    assert resolve_route(policy, query) == resolve_route(policy, query)


def test_validate_deterministic(tmp_path) -> None:
    policy_path = seed_routing_repo(tmp_path)
    first = validate_routing_policy(policy_path, kit_root=kit_root())
    second = validate_routing_policy(policy_path, kit_root=kit_root())
    assert first == second


def test_routing_policy_in_footprint(git_only_config) -> None:
    dests = {item.destination for item in resolve_footprint(git_only_config)}
    assert ".overseer/policy/model-routing.yaml" in dests
    assert ".overseer/policy/model-labels.yaml" in dests


def test_validate_does_not_mutate_policy_file(tmp_path) -> None:
    policy_path = seed_routing_repo(tmp_path)
    before = policy_path.read_bytes()
    run_cli(
        ["route", "--validate"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    after = policy_path.read_bytes()
    assert before == after

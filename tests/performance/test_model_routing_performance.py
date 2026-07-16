"""Performance tests for Track P / P-route (§PR.8)."""

from __future__ import annotations

import time
from unittest.mock import patch

from cli.kit_root import kit_root
from tests.fixtures.model_routing import seed_routing_repo
from tests.support import git_status_runner, run_cli
from tools.model_routing.policy import validate_routing_policy

BOUND_MS = 500


def test_route_resolve_bounded(tmp_path) -> None:
    seed_routing_repo(tmp_path)
    start = time.perf_counter()
    code = run_cli(
        ["route", "--position", "worker", "--gate", "default"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert code == 0
    assert elapsed_ms < BOUND_MS


def test_route_validate_bounded(tmp_path) -> None:
    policy_path = seed_routing_repo(tmp_path)
    start = time.perf_counter()
    result = validate_routing_policy(policy_path, kit_root=kit_root())
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert result.valid is True
    assert elapsed_ms < BOUND_MS


def test_route_does_not_scan_vcs(tmp_path) -> None:
    seed_routing_repo(tmp_path)
    with patch("cli.vcs_status.read_vcs_status") as mocked:
        mocked.side_effect = AssertionError("route must not scan VCS")
        code = run_cli(
            ["route", "--validate"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
    assert code == 0

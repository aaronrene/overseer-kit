"""Security tests for Track P / P-route (§PR.8)."""

from __future__ import annotations

import inspect
import json
import socket
from pathlib import Path
from unittest.mock import patch

import pytest

from cli.kit_root import kit_root
from tests.fixtures.model_routing import seed_routing_repo, write_routing_policy
from tests.support import git_status_runner, run_cli
from tools.model_routing import policy as routing_policy_module
from tools.model_routing import resolve as routing_resolve_module


class _SocketBlockedError(RuntimeError):
    pass


@pytest.fixture
def block_network():
    real_socket = socket.socket

    def _guard(*args, **kwargs):
        raise _SocketBlockedError("network connections forbidden in routing code paths")

    with patch.object(socket, "socket", side_effect=_guard):
        yield


def test_route_makes_no_network_connections(tmp_path, block_network) -> None:
    seed_routing_repo(tmp_path)
    code = run_cli(
        ["route", "--position", "overseer", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0


def test_injection_shaped_selector_strings_are_opaque(tmp_path, capsys, block_network) -> None:
    seed_routing_repo(tmp_path)
    payload = "'; DROP TABLE routes; --"
    code = run_cli(
        ["route", "--position", payload, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["query"]["position"] == payload
    assert out["route_id"] == "defaults"


def test_route_output_has_no_vendor_slugs(tmp_path, capsys) -> None:
    seed_routing_repo(tmp_path)
    run_cli(
        ["route", "--phase-tier", "auto", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    text = capsys.readouterr().out.lower()
    for marker in ("gpt-", "claude-", "openrouter", "api_key", "sk-"):
        assert marker not in text


def test_malformed_policy_exit_30_missing_human_terminal(tmp_path) -> None:
    seed_routing_repo(tmp_path)
    write_routing_policy(
        tmp_path,
        """
version: 1
defaults:
  model_tier: standard
  fallback: [standard, fast]
""",
    )
    assert (
        run_cli(
            ["route", "--validate"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 30
    )


def test_missing_policy_exit_31(tmp_path) -> None:
    from tests.support import write_config

    write_config(tmp_path, "config-git-only.yaml")
    assert (
        run_cli(
            ["route"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 31
    )


def test_routing_modules_avoid_http_clients() -> None:
    sources = (
        inspect.getsource(routing_policy_module),
        inspect.getsource(routing_resolve_module),
    )
    joined = "\n".join(sources).lower()
    assert "urllib" not in joined
    assert "requests." not in joined
    assert "httpx" not in joined

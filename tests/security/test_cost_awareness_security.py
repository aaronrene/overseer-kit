"""Security tests for Track P / P-cost (§PC.9)."""

from __future__ import annotations

import inspect
import json
import socket
from pathlib import Path
from unittest.mock import patch

import pytest

from cli.kit_root import kit_root
from tests.fixtures.cost_awareness import seed_cost_awareness_repo, seed_cost_e2e_repo
from tests.support import git_status_runner, run_cli
from tools import cost_awareness


class _SocketBlockedError(RuntimeError):
    pass


@pytest.fixture
def block_network():
    real_socket = socket.socket

    def _guard(*args, **kwargs):
        raise _SocketBlockedError("network connections forbidden in cost-awareness paths")

    with patch.object(socket, "socket", side_effect=_guard):
        yield


def test_cost_paths_make_no_network_connections(tmp_path, block_network) -> None:
    seed_cost_e2e_repo(tmp_path)
    code = run_cli(
        ["route", "--phase-tier", "auto", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0


def test_cost_output_has_no_currency_or_price_markers(tmp_path, capsys) -> None:
    seed_cost_e2e_repo(tmp_path)
    run_cli(
        ["route", "--phase-tier", "auto", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    text = capsys.readouterr().out.lower()
    for marker in ("$", "usd", "eur", "price", "budget", "gpt-", "openrouter"):
        assert marker not in text


def test_injection_shaped_cost_class_fail_closed(tmp_path, monkeypatch) -> None:
    seed_cost_awareness_repo(tmp_path, enabled=False)
    from tools.model_routing.labels import RoutingPolicyError

    def _raise(*args, **kwargs):
        raise RoutingPolicyError("'; DROP TABLE tiers; --", exit_code=32)

    monkeypatch.setattr("cli.commands.route.load_model_tier_cost_bands", _raise)
    assert (
        run_cli(
            ["route"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 32
    )


def test_cost_surface_reminder_only_never_blocks_success(tmp_path, capsys) -> None:
    seed_cost_e2e_repo(tmp_path)
    code = run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["cost_awareness"]["enabled"] is True


def test_cost_modules_do_not_import_network_clients() -> None:
    forbidden = ("urllib", "http.client", "requests", "httpx")
    for module in (
        cost_awareness.derive,
        cost_awareness.surface,
        cost_awareness.format,
        cost_awareness.normalize,
    ):
        source = inspect.getsource(module)
        for token in forbidden:
            assert token not in source

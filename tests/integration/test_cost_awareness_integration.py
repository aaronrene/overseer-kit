"""Integration tests for Track P / P-cost CLI (§PC.9)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from cli.kit_root import kit_root
from tests.fixtures.cost_awareness import seed_cost_awareness_repo
from tests.fixtures.model_routing import seed_routing_repo
from tests.support import FIXTURES, git_status_runner, run_cli
from tools.model_routing.labels import RoutingPolicyError


def _write_lock(repo_root: Path) -> None:
    (repo_root / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:0\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
    )


def test_route_emits_cost_annotation(tmp_path: Path, capsys) -> None:
    seed_routing_repo(tmp_path)
    code = run_cli(
        ["route", "--phase-tier", "auto", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["route_id"] == "auto-build"
    assert payload["model_tier"] == "standard"
    assert payload["cost_class"] == "moderate"
    assert payload["paid_step_before_spend"] is True


def test_route_resolution_unchanged_with_cost_fields(tmp_path: Path, capsys) -> None:
    seed_routing_repo(tmp_path)
    run_cli(
        ["route", "--position", "overseer", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["route_id"] == "overseer-ruling"
    assert payload["model_tier"] == "deep-reasoning"
    assert payload["fallback"] == ["deep-reasoning", "human"]


def test_route_malformed_cost_class_exit_32(tmp_path: Path, monkeypatch) -> None:
    seed_routing_repo(tmp_path)

    def _raise(*args, **kwargs):
        raise RoutingPolicyError("bad cost_class", exit_code=32)

    monkeypatch.setattr("cli.commands.route.load_model_tier_cost_bands", _raise)
    assert (
        run_cli(
            ["route", "--phase-tier", "auto"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 32
    )


def test_status_disabled_byte_identical_no_cost_key(tmp_path: Path, capsys) -> None:
    seed_cost_awareness_repo(tmp_path, enabled=False)
    _write_lock(tmp_path)
    code = run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "cost_awareness" not in payload


def test_status_enabled_emits_cost_surface(tmp_path: Path, capsys) -> None:
    from tests.fixtures.cost_awareness import seed_cost_e2e_repo

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
    assert payload["cost_awareness"]["slices"]


def test_status_missing_policy_exit_31(tmp_path: Path) -> None:
    from tests.support import write_config

    write_config(tmp_path, "config-git-only.yaml")
    cfg_path = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["cost_awareness"] = {"enabled": True}
    cfg_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    _write_lock(tmp_path)
    assert (
        run_cli(
            ["status"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 31
    )


def test_status_invalid_cost_metadata_warning_only(tmp_path: Path, capsys, monkeypatch) -> None:
    seed_cost_awareness_repo(tmp_path, enabled=True)
    _write_lock(tmp_path)
    from tests.fixtures.model_routing import copy_default_routing_policy

    copy_default_routing_policy(tmp_path)

    def _raise(*args, **kwargs):
        raise RoutingPolicyError("bad cost_class", exit_code=32)

    monkeypatch.setattr(
        "tools.cost_awareness.surface.load_model_tier_cost_bands",
        _raise,
    )
    code = run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["cost_awareness"]["invalid"] is True
    assert any("cost_awareness: invalid" in warning for warning in payload["warnings"])

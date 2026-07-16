"""Integration tests for Track P / P-route CLI (§PR.8)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.kit_root import kit_root
from tests.fixtures.model_routing import seed_routing_repo, write_routing_policy
from tests.support import FIXTURES, git_status_runner, run_cli, write_config


def test_route_resolves_representative_triple(tmp_path: Path) -> None:
    seed_routing_repo(tmp_path)
    code = run_cli(
        ["route", "--position", "overseer", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0


def test_route_json_payload(tmp_path: Path, capsys) -> None:
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
    assert payload["fallback"] == ["standard", "human"]


def test_route_validate_valid(tmp_path: Path) -> None:
    seed_routing_repo(tmp_path)
    assert (
        run_cli(
            ["route", "--validate"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 0
    )


def test_route_validate_reports_first_violation(tmp_path: Path) -> None:
    seed_routing_repo(tmp_path)
    write_routing_policy(
        tmp_path,
        """
version: 1
defaults:
  model_tier: standard
  fallback: [fast, human]
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


def test_route_missing_policy_exit_31(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    assert (
        run_cli(
            ["route", "--validate"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 31
    )


def test_route_malformed_policy_exit_30(tmp_path: Path) -> None:
    seed_routing_repo(tmp_path)
    write_routing_policy(
        tmp_path,
        """
version: 1
defaults:
  model_tier: standard
  fallback: [standard]
""",
    )
    assert (
        run_cli(
            ["route"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 30
    )


def test_model_routing_enabled_false_status_unchanged(tmp_path: Path, capsys) -> None:
    seed_routing_repo(tmp_path, enabled=False)
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:0\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
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
    assert payload["model_routing"]["enabled"] is False


def test_model_routing_enabled_true_shows_validity(tmp_path: Path, capsys) -> None:
    seed_routing_repo(tmp_path, enabled=True)
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:0\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
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
    assert payload["model_routing"]["enabled"] is True
    assert payload["model_routing"]["valid"] is True


def test_model_routing_policy_path_escape_exit_4(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["model_routing"] = {"enabled": True, "policy": "../outside.yaml"}
    cfg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(cfg)
    data["model_routing"] = {"enabled": True, "policy": "policy/model-routing.yaml"}
    cfg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    seed_routing_repo(tmp_path)
    data["model_routing"] = {"enabled": True, "policy": "/etc/passwd"}
    cfg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(ConfigError, match="repo-relative"):
        load_config(cfg)


def test_config_model_routing_defaults() -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    assert config.model_routing.enabled is False
    assert config.model_routing.policy == "policy/model-routing.yaml"

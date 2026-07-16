"""End-to-end tests for Track P / P-route (§PR.8)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.footprint import resolve_footprint
from cli.kit_root import kit_root
from tests.fixtures.model_routing import seed_routing_repo
from tests.support import FIXTURES, git_status_runner, load_fixture_config, run_cli


def _seed_lock(tmp_path: Path) -> None:
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:0\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
    )


def test_e2e_resolve_cycle(tmp_path: Path, capsys) -> None:
    seed_routing_repo(tmp_path)
    cases = [
        (["--position", "overseer"], "overseer-ruling", "deep-reasoning"),
        (["--phase-tier", "auto"], "auto-build", "standard"),
        (["--position", "nobody"], "defaults", "standard"),
    ]
    for argv, route_id, tier in cases:
        code = run_cli(
            ["route", *argv, "--json"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            json_mode=True,
        )
        assert code == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["route_id"] == route_id
        assert payload["model_tier"] == tier


def test_e2e_identical_under_git_only_and_muse_regime(tmp_path: Path, capsys) -> None:
    for config_name in ("config-git-only.yaml", "config-muse-only.yaml"):
        repo = tmp_path / config_name
        repo.mkdir()
        seed_routing_repo(repo, config_name=config_name)
        code = run_cli(
            ["route", "--gate", "build_verification", "--json"],
            cwd=repo,
            runner=git_status_runner(),
            kit=kit_root(),
            json_mode=True,
        )
        assert code == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["route_id"] == "build-verification"


def test_e2e_status_routing_validity_only_when_enabled(tmp_path: Path, capsys) -> None:
    seed_routing_repo(tmp_path, enabled=False)
    _seed_lock(tmp_path)
    run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    disabled = json.loads(capsys.readouterr().out)
    assert disabled["model_routing"]["enabled"] is False

    cfg = tmp_path / ".overseer" / "config.yaml"
    import yaml

    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["model_routing"] = {"enabled": True, "policy": "policy/model-routing.yaml"}
    cfg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    enabled = json.loads(capsys.readouterr().out)
    assert enabled["model_routing"]["enabled"] is True
    assert "valid" in enabled["model_routing"]


def test_footprint_includes_model_routing_policy(git_only_config) -> None:
    dests = {f.destination for f in resolve_footprint(git_only_config)}
    assert ".overseer/policy/model-routing.yaml" in dests

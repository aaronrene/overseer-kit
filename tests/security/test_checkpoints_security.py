"""Security tests for checkpoint path discipline and JSON emission."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from cli.kit_root import kit_root
from tests.support import git_status_runner, run_cli, seed_checkpoint_repo


def test_manifest_path_escape_refused(tmp_path: Path, capsys) -> None:
    seed_checkpoint_repo(tmp_path)
    code = run_cli(
        ["verify-step", "--step", "alpha", "--manifest", "../../../etc/passwd", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 4
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 4
    manifest = payload.get("manifest") or ""
    assert not manifest.startswith("/")


def test_json_emits_on_nonzero_usage(tmp_path: Path, capsys) -> None:
    seed_checkpoint_repo(tmp_path)
    code = run_cli(
        ["verify-step", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error"] == "usage"
    assert payload["dry_run"] is False


def test_disabled_module_json_without_manifest(tmp_path: Path, capsys) -> None:
    from tests.support import write_config

    write_config(tmp_path, "config-git-only.yaml")
    code = run_cli(
        ["verify-step", "--step", "alpha", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 4
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 4


def test_policy_escape_refused(tmp_path: Path) -> None:
    seed_checkpoint_repo(tmp_path)
    code = run_cli(
        ["verify-step", "--step", "alpha", "--policy", "/etc/passwd"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4

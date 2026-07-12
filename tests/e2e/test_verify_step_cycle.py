"""End-to-end verify-step CLI tests."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from cli.kit_root import kit_root
from tests.support import CHECKPOINTS, git_status_runner, run_cli, seed_checkpoint_repo


def test_cli_step_pass_updates_manifest(tmp_path: Path, capsys) -> None:
    seed_checkpoint_repo(tmp_path)
    code = run_cli(
        ["verify-step", "--step", "alpha", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["dry_run"] is False
    manifest = yaml.safe_load((tmp_path / "manifests" / "work-unit.yaml").read_text(encoding="utf-8"))
    assert manifest["steps"]["alpha"]["verified"] is True


def test_cli_verify_fail_exit_10(tmp_path: Path) -> None:
    seed_checkpoint_repo(tmp_path)
    manifest_path = tmp_path / "manifests" / "work-unit.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    data["template_id"] = "three_step"
    data["current_step"] = "gamma"
    data["steps"]["alpha"]["verified"] = True
    data["steps"]["beta"]["verified"] = True
    data["steps"]["gamma"] = {"verified": False, "verified_at": None, "artifact_sha256": None}
    manifest_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    before = manifest_path.read_bytes()
    code = run_cli(
        ["verify-step", "--step", "gamma"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 10
    assert manifest_path.read_bytes() == before


def test_cli_all_happy_path(tmp_path: Path) -> None:
    seed_checkpoint_repo(tmp_path)
    code = run_cli(
        ["verify-step", "--all"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 0
    manifest = yaml.safe_load((tmp_path / "manifests" / "work-unit.yaml").read_text(encoding="utf-8"))
    assert manifest["steps"]["alpha"]["verified"] is True
    assert manifest["steps"]["beta"]["verified"] is True


def test_cli_through_current_all_verified_noop(tmp_path: Path, capsys) -> None:
    seed_checkpoint_repo(tmp_path)
    (tmp_path / "manifests" / "work-unit.yaml").write_text(
        (CHECKPOINTS / "manifests" / "all-verified.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    code = run_cli(
        ["verify-step", "--through", "current", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["steps"] == []


def test_cli_dry_run_leaves_manifest_unchanged(tmp_path: Path) -> None:
    seed_checkpoint_repo(tmp_path)
    manifest_path = tmp_path / "manifests" / "work-unit.yaml"
    before = manifest_path.read_bytes()
    code = run_cli(
        ["verify-step", "--step", "alpha", "--dry-run"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 0
    assert manifest_path.read_bytes() == before

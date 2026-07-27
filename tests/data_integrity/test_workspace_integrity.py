"""Data-integrity tests for workspace lanes (§MR.10 data-integrity)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from tools.workspace.check_next import build_status_report, check_next
from tools.workspace.manifest import discover_manifest, load_manifest_file
from tools.workspace.types import WorkspaceLoadError
from tests.fixtures.workspace import build_two_repo_constellation


def test_readonly_commands_do_not_mutate(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    before = {
        p: p.read_bytes()
        for p in fx["scooling"].rglob("*")
        if p.is_file()
    }
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    build_status_report(cfg, fx["scooling"])
    manifest = load_manifest_file(fx["manifest"], manifest_source="local_workspace")
    check_next(manifest)
    after = {
        p: p.read_bytes()
        for p in fx["scooling"].rglob("*")
        if p.is_file()
    }
    assert before == after


def test_twice_run_identical_outputs(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    a = build_status_report(cfg, fx["scooling"]).to_json()
    b = build_status_report(cfg, fx["scooling"]).to_json()
    assert a == b


def test_tip_hash_stable(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    manifest = load_manifest_file(fx["manifest"], manifest_source="local_workspace")
    r1 = check_next(manifest)
    r2 = check_next(manifest)
    assert r1.primary is not None and r2.primary is not None
    assert r1.primary["tip_hash"] == r2.primary["tip_hash"] == fx["tip_hash"]


def test_missing_required_member_fail_closed(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    # Point knowtation root at empty path
    text = fx["manifest"].read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    for m in data["members"]:
        if m["id"] == "knowtation":
            m["root"] = str(tmp_path / "missing-knowtation")
    fx["manifest"].write_text(yaml.safe_dump(data), encoding="utf-8")
    manifest = load_manifest_file(fx["manifest"], manifest_source="local_workspace")
    result = check_next(manifest)
    assert result.exit_code == 35
    assert result.state == "missing_member"


def test_override_manifest_id_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fx = build_two_repo_constellation(tmp_path)
    other = tmp_path / "other-manifest.yaml"
    data = yaml.safe_load(fx["manifest"].read_text(encoding="utf-8"))
    data["id"] = "wrong-id"
    other.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.setenv("OVERSEER_WORKSPACE_MANIFEST", str(other))
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    with pytest.raises(WorkspaceLoadError):
        discover_manifest(cfg, fx["scooling"], environ=dict(os.environ))

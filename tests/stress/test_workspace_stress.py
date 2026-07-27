"""Stress tests for workspace lanes (§MR.10 stress)."""

from __future__ import annotations

import json
import time
from pathlib import Path

import yaml

from tools.workspace.manifest import validate_manifest_dict
from tools.workspace.check_next import check_next, build_status_report
from tools.workspace.manifest import load_manifest_file
from tests.fixtures.workspace import build_two_repo_constellation
from adapters.config import load_config


def test_large_manifest_bounded(tmp_path: Path) -> None:
    members = []
    for i in range(25):
        members.append(
            {
                "id": f"m{i}",
                "role": "product_order" if i == 0 else "other",
                "root": str(tmp_path / f"m{i}"),
                "regime": "git-only",
                "required": False,
                "relay": False,
            }
        )
    lanes = [{"id": f"lane{i}", "primary": i == 0} for i in range(12)]
    raw = {
        "overseer_workspace_version": 1,
        "id": "big",
        "product_order_member": "m0",
        "members": members,
        "lanes": lanes,
    }
    start = time.perf_counter()
    manifest = validate_manifest_dict(
        raw, source_path=tmp_path / "workspace.yaml", manifest_source="local_workspace"
    )
    elapsed = time.perf_counter() - start
    assert len(manifest.members) == 25
    assert len(manifest.lanes) == 12
    assert elapsed < 1.0


def test_status_json_key_order_stable(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    a = json.dumps(build_status_report(cfg, fx["scooling"]).to_json(), sort_keys=True)
    b = json.dumps(build_status_report(cfg, fx["scooling"]).to_json(), sort_keys=True)
    assert a == b

"""Integration tests for Track Q / Q2b OK CLI entrypoint (§Q2A.10)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.support import OVERSEER_DEPRECATION_LINE, run_cli, run_shim, seed_git_repo, write_config


def test_ok_and_overseer_shims_emit_equivalent_status_json(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    write_config(tmp_path, "config-git-only.yaml")
    run_cli(["init", "--regime", "git-only", "--non-interactive", "--force"], cwd=tmp_path)

    ok_result = run_shim("ok", ["status", "--json"], cwd=tmp_path)
    overseer_result = run_shim("overseer", ["status", "--json"], cwd=tmp_path)

    assert ok_result.exit_code == overseer_result.exit_code == 0
    assert ok_result.stderr == ""
    assert overseer_result.stderr == OVERSEER_DEPRECATION_LINE

    ok_payload = json.loads(ok_result.stdout)
    overseer_payload = json.loads(overseer_result.stdout)
    assert set(ok_payload.keys()) == set(overseer_payload.keys())
    assert ok_payload.get("initialized") == overseer_payload.get("initialized")

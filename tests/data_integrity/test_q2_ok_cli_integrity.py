"""Data-integrity tests for Track Q / Q2b OK CLI entrypoint (§Q2A.10)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.footprint import resolve_footprint
from tests.support import load_fixture_config, run_cli, run_shim, seed_git_repo, write_config


def test_ok_status_json_is_idempotent(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    write_config(tmp_path, "config-git-only.yaml")
    run_cli(["init", "--regime", "git-only", "--non-interactive", "--force"], cwd=tmp_path)

    first = run_shim("ok", ["status", "--json"], cwd=tmp_path)
    second = run_shim("ok", ["status", "--json"], cwd=tmp_path)
    assert first.exit_code == second.exit_code == 0
    first_payload = json.loads(first.stdout)
    second_payload = json.loads(second.stdout)
    for key in ("initialized", "kit_version", "lock"):
        assert first_payload.get(key) == second_payload.get(key)


def test_shims_are_not_footprint_members(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    destinations = {item.destination for item in resolve_footprint(config)}
    assert "cli/ok" not in destinations
    assert "cli/overseer" not in destinations


def test_version_lock_never_lists_shim_paths(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    write_config(tmp_path, "config-git-only.yaml")
    run_cli(["init", "--regime", "git-only", "--non-interactive", "--force"], cwd=tmp_path)
    lock_path = tmp_path / ".overseer" / "version.lock"
    lock_text = lock_path.read_text(encoding="utf-8")
    assert "cli/ok" not in lock_text
    assert "cli/overseer" not in lock_text

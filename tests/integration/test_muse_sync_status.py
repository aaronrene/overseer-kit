"""Integration tests: adapters surface muse_dirty/git_dirty; status wires the gate (§KH2.5)."""

from __future__ import annotations

import json
from pathlib import Path

from adapters.errors import ReadError
from tests.support import (
    FIXTURES,
    adapter_for,
    make_runner,
    ok,
    run_cli,
    seed_governance_freshness,
    seed_muse_substrate,
)


def _init(tmp_path: Path, runner, config_name: str) -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / config_name), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    seed_governance_freshness(tmp_path)


def test_mirror_adapter_populates_both_dirty_fields(muse_git_mirror_config, repo_root: Path) -> None:
    root = str(repo_root.resolve())
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": true}'),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    status = adapter.status()
    assert not isinstance(status, ReadError)
    assert status.muse_dirty is True
    assert status.git_dirty is False
    assert status.dirty is True  # combined flag unchanged in meaning


def test_muse_only_adapter_leaves_git_dirty_none(muse_only_config, repo_root: Path) -> None:
    root = str(repo_root.resolve())
    runner = make_runner(
        {
            f"muse -C {root} branch --show-current": ok("main"),
            f"muse -C {root} status --porcelain": ok(""),
        }
    )
    adapter = adapter_for(muse_only_config, repo_root, runner)
    status = adapter.status()
    assert not isinstance(status, ReadError)
    assert status.muse_dirty is False
    assert status.git_dirty is None


def test_git_only_adapter_leaves_muse_dirty_none(git_only_config, repo_root: Path) -> None:
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(" M file"),
        }
    )
    adapter = adapter_for(git_only_config, repo_root, runner)
    status = adapter.status()
    assert not isinstance(status, ReadError)
    assert status.muse_dirty is None
    assert status.git_dirty is True


def test_status_exit_code_2_when_muse_pending(tmp_path: Path) -> None:
    root = str(tmp_path.resolve())
    tip = "cafebabe"
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": true}'),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok(tip),
            f"muse -C {root} rev-parse main": ok(tip),
        }
    )
    _init(tmp_path, runner, "config-muse-git-mirror.yaml")
    seed_muse_substrate(tmp_path)
    code = run_cli(["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True)
    assert code == 2


def test_status_exit_code_0_when_muse_synced(tmp_path: Path) -> None:
    root = str(tmp_path.resolve())
    tip = "cafebabe"
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": false}'),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok(tip),
            f"muse -C {root} rev-parse main": ok(tip),
        }
    )
    _init(tmp_path, runner, "config-muse-git-mirror.yaml")
    seed_muse_substrate(tmp_path)
    code = run_cli(["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True)
    assert code == 0


def test_status_json_payload_reports_muse_sync_state(tmp_path: Path, capsys) -> None:
    root = str(tmp_path.resolve())
    tip = "cafebabe"
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": true}'),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok(tip),
            f"muse -C {root} rev-parse main": ok(tip),
        }
    )
    _init(tmp_path, runner, "config-muse-git-mirror.yaml")
    seed_muse_substrate(tmp_path)
    capsys.readouterr()  # discard `init` output before capturing the status payload
    run_cli(["status", "--json"], cwd=tmp_path, runner=runner, json_mode=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["muse_sync"]["state"] == "pending"
    assert payload["muse_sync"]["ok"] is False
    assert "muse commit" in payload["muse_sync"]["remediation"]

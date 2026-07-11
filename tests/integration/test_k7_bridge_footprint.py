"""Integration tests for K7 bridge footprint init/sync/status (§K7.8 integration tier)."""

from __future__ import annotations

import stat
from pathlib import Path

from adapters.config import load_config
from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST, MUSE_BRIDGE_WORKFLOW_DEST
from cli.footprint_writes import FOOTPRINT_EXECUTABLE_MODE
from cli.kit_root import kit_root
from cli.version_lock import read_version_lock
from tests.support import FIXTURES, git_status_runner, muse_mirror_status_runner, run_cli


def _init_mirror(tmp_path: Path) -> None:
    code = run_cli(
        [
            "init",
            "--from-config",
            str(FIXTURES / "config-muse-git-mirror.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0


def test_muse_git_mirror_init_writes_bridge_files_executable(tmp_path: Path) -> None:
    _init_mirror(tmp_path)
    workflow = tmp_path / MUSE_BRIDGE_WORKFLOW_DEST
    script = tmp_path / MUSE_BRIDGE_DEPLOY_DEST
    assert workflow.is_file()
    assert script.is_file()
    assert stat.S_IMODE(script.stat().st_mode) == FOOTPRINT_EXECUTABLE_MODE
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    paths = {e.path for e in lock.footprint}
    assert MUSE_BRIDGE_WORKFLOW_DEST in paths
    assert MUSE_BRIDGE_DEPLOY_DEST in paths


def test_git_only_init_has_no_bridge_files(tmp_path: Path) -> None:
    code = run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
        kit=kit_root(),
    )
    assert code == 0
    assert not (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).exists()
    assert not (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).exists()


def test_muse_mirror_status_check_footprint_ok(tmp_path: Path) -> None:
    _init_mirror(tmp_path)
    code = run_cli(
        ["status", "--check-footprint"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0


def test_sync_noop_at_same_version_with_bridge_files(tmp_path: Path) -> None:
    _init_mirror(tmp_path)
    code = run_cli(
        ["sync", "-y"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0


def test_migrate_conflict_on_differing_preexisting_deploy_script(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "muse-bridge-deploy.sh").write_text("#!/bin/bash\necho hand-tuned\n", encoding="utf-8")
    (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).write_text("# hand workflow\n", encoding="utf-8")
    code = run_cli(
        [
            "init",
            "--migrate",
            "--from-config",
            str(FIXTURES / "config-muse-git-mirror.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 4


def test_sync_seeds_new_bridge_destinations_when_absent_from_lock(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
        kit=kit_root(),
    )
    mirror_cfg = (FIXTURES / "config-muse-git-mirror.yaml").read_text(encoding="utf-8")
    (tmp_path / ".overseer" / "config.yaml").write_text(mirror_cfg, encoding="utf-8")
    assert not (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).exists()
    assert not (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).exists()
    code = run_cli(
        ["sync", "-y"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0
    assert (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).is_file()
    assert (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).is_file()
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert MUSE_BRIDGE_DEPLOY_DEST in {e.path for e in lock.footprint}


def test_sync_conflicts_when_bridge_on_disk_not_in_lock(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
        kit=kit_root(),
    )
    mirror_cfg = (FIXTURES / "config-muse-git-mirror.yaml").read_text(encoding="utf-8")
    (tmp_path / ".overseer" / "config.yaml").write_text(mirror_cfg, encoding="utf-8")
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "muse-bridge-deploy.sh").write_text("#!/bin/bash\necho consumer\n", encoding="utf-8")
    (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).write_text("# consumer workflow\n", encoding="utf-8")
    code = run_cli(
        ["sync", "-y"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 4


def test_overseer_kit_dogfood_fixture_init(tmp_path: Path) -> None:
    code = run_cli(
        [
            "init",
            "--from-config",
            str(FIXTURES / "config-overseer-kit-dogfood.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    assert config.repo.name == "overseer-kit"
    assert config.docs.coordination is None
    assert (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).is_file()

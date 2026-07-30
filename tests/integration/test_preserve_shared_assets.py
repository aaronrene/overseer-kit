"""Integration — preserve shared bridge assets on migrate (§PSA.8)."""

from __future__ import annotations

from pathlib import Path

from cli.digest import sha256_hex
from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST, MUSE_BRIDGE_WORKFLOW_DEST
from cli.kit_root import kit_root
from cli.version_lock import ORIGIN_KIT, ORIGIN_PRESERVED, read_version_lock
from tests.support import FIXTURES, muse_mirror_status_runner, run_cli


HAND_SCRIPT = "#!/bin/bash\necho knowtation-bridge\n# consumer-owned\n"
HAND_WORKFLOW = "# Knowtation MUSE-BRIDGE-WORKFLOW\nconsumer owned\n"


def _seed_hand_bridge(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "muse-bridge-deploy.sh").write_text(HAND_SCRIPT, encoding="utf-8")
    (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).write_text(HAND_WORKFLOW, encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text("# hand handover\n", encoding="utf-8")
    (tmp_path / "docs" / "ROADMAP.md").write_text("# hand roadmap\n", encoding="utf-8")


def test_migrate_preserve_shared_keeps_bridge_bytes(tmp_path: Path) -> None:
    _seed_hand_bridge(tmp_path)
    code = run_cli(
        [
            "init",
            "--migrate",
            "--force",
            "--preserve-shared-assets",
            "--from-config",
            str(FIXTURES / "config-muse-git-mirror.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0
    assert (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).read_text(encoding="utf-8") == HAND_SCRIPT
    assert (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).read_text(encoding="utf-8") == HAND_WORKFLOW
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    by_path = {e.path: e for e in lock.footprint}
    assert by_path[MUSE_BRIDGE_DEPLOY_DEST].origin == ORIGIN_PRESERVED
    assert by_path[MUSE_BRIDGE_WORKFLOW_DEST].origin == ORIGIN_PRESERVED
    assert by_path[MUSE_BRIDGE_DEPLOY_DEST].sha256 == sha256_hex(HAND_SCRIPT.encode())


def test_migrate_force_without_preserve_overwrites_bridge(tmp_path: Path) -> None:
    _seed_hand_bridge(tmp_path)
    code = run_cli(
        [
            "init",
            "--migrate",
            "--force",
            "--from-config",
            str(FIXTURES / "config-muse-git-mirror.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0
    assert (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).read_text(encoding="utf-8") != HAND_SCRIPT
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    by_path = {e.path: e for e in lock.footprint}
    assert by_path[MUSE_BRIDGE_DEPLOY_DEST].origin == ORIGIN_KIT

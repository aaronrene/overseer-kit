"""E2E — preserve shared assets then status/sync retain (§PSA.8)."""

from __future__ import annotations

from pathlib import Path

from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST, MUSE_BRIDGE_WORKFLOW_DEST
from cli.kit_root import kit_root
from tests.support import FIXTURES, muse_mirror_status_runner, run_cli


HAND_SCRIPT = "#!/bin/bash\necho e2e-consumer-bridge\n"
HAND_WORKFLOW = "# e2e consumer workflow\n"


def test_preserve_migrate_force_footprint_ok_and_sync_retains(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "muse-bridge-deploy.sh").write_text(HAND_SCRIPT, encoding="utf-8")
    (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).write_text(HAND_WORKFLOW, encoding="utf-8")
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text("# H\n", encoding="utf-8")
    (tmp_path / "docs" / "ROADMAP.md").write_text("# R\n", encoding="utf-8")

    runner = muse_mirror_status_runner(tmp_path)
    assert (
        run_cli(
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
            runner=runner,
        )
        == 0
    )
    assert run_cli(["status", "--check-footprint"], cwd=tmp_path, runner=runner) == 0
    assert run_cli(["sync", "-y"], cwd=tmp_path, runner=runner) == 0
    assert (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).read_text(encoding="utf-8") == HAND_SCRIPT
    assert (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).read_text(encoding="utf-8") == HAND_WORKFLOW

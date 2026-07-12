"""E2E fixture dogfood cycle for K7 bridge footprint (§K7.8 e2e tier)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST, MUSE_BRIDGE_WORKFLOW_DEST
from tests.support import FIXTURES, muse_mirror_status_runner, ok, run_cli, seed_muse_substrate


def test_k7_fixture_dogfood_cycle_no_live_muse(tmp_path: Path) -> None:
    runner = muse_mirror_status_runner(tmp_path)
    root = str(tmp_path.resolve())
    runner.responses.update(
        {
            f"muse -C {root} log -1 --format=%H main": ok("a" * 40),
            "git rev-parse origin/main": ok("b" * 40),
            "git rev-parse origin/muse-mirror": ok("c" * 40),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                json.dumps([])
            ),
        }
    )
    seed_muse_substrate(tmp_path)
    (tmp_path / ".muse" / "git-bridge.toml").write_text(
        '[last_export]\ngit_sha = "' + ("d" * 40) + '"\n'
        '[last_import]\ngit_sha = "' + ("d" * 40) + '"\n',
        encoding="utf-8",
    )
    assert (
        run_cli(
            [
                "init",
                "--from-config",
                str(FIXTURES / "config-overseer-kit-dogfood.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    assert (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).is_file()
    assert (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).is_file()
    assert run_cli(["status", "--check-footprint"], cwd=tmp_path, runner=runner) == 0
    assert run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner) == 0
    assert run_cli(["sync", "-y"], cwd=tmp_path, runner=runner) == 0
    muse_calls = [c for c in runner.calls if "bridge git-export" in c[0]]
    assert muse_calls == []

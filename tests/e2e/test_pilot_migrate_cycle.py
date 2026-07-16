"""E2E migrate cycle on pilot fixtures (§K6.10)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.version_lock import ORIGIN_PRESERVED
from tests.support import (
    PILOT,
    lock_origins,
    muse_mirror_status_runner,
    ok,
    run_cli,
    seed_pilot_tree,
    seed_muse_substrate,
)


def test_pilot_migrate_cycle_preserves_and_seeds(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# pre-existing handover ≠ template\n",
        roadmap_rel=None,
    )
    runner = muse_mirror_status_runner(tmp_path)
    root = str(tmp_path.resolve())
    runner.responses.update(
        {
            f"muse -C {root} rev-parse main": ok("a" * 40),
            "git rev-parse origin/main": ok("b" * 40),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                json.dumps([])
            ),
        }
    )
    seed_muse_substrate(tmp_path)
    (tmp_path / ".muse" / "git-bridge.toml").write_text(
        '[last_export]\ngit_sha = "' + ("c" * 40) + '"\n'
        '[last_import]\ngit_sha = "' + ("c" * 40) + '"\n',
        encoding="utf-8",
    )

    code = run_cli(
        [
            "init",
            "--migrate",
            "--from-config",
            str(PILOT / "config-knowtation.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        runner=runner,
    )
    assert code == 0
    assert (
        tmp_path / "docs/OVERSEER-HANDOVER.md"
    ).read_text(encoding="utf-8") == "# pre-existing handover ≠ template\n"
    assert (tmp_path / "docs/ROADMAP.md").is_file()
    origins = lock_origins(tmp_path)
    assert origins["docs/OVERSEER-HANDOVER.md"] == ORIGIN_PRESERVED
    assert origins["docs/ROADMAP.md"] == ORIGIN_PRESERVED
    assert (tmp_path / ".overseer/policy/tiers.yaml").is_file()
    assert (tmp_path / ".cursor/rules/governance-sync.mdc").is_file()

    assert run_cli(["status", "--check-footprint"], cwd=tmp_path, runner=runner) == 0

    # Second migrate no-op while config + lock + on-disk still match
    lock_before = (tmp_path / ".overseer/version.lock").read_text(encoding="utf-8")
    code2 = run_cli(
        [
            "init",
            "--migrate",
            "--from-config",
            str(PILOT / "config-knowtation.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        runner=runner,
    )
    assert code2 == 0
    assert (tmp_path / ".overseer/version.lock").read_text(encoding="utf-8") == lock_before

    # Hand-edit seeded roadmap leaves check-footprint ok
    (tmp_path / "docs/ROADMAP.md").write_text("# seeded hand-edit\n", encoding="utf-8")
    assert run_cli(["status", "--check-footprint"], cwd=tmp_path, runner=runner) == 0

    gs = run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner)
    assert gs == 0
    assert (tmp_path / "docs/ROADMAP.md").read_text(encoding="utf-8") == "# seeded hand-edit\n"

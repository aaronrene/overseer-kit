"""E2E: the muse-sync hard gate blocks then clears across review + governance-sync (§KH2.8 e2e tier)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    ok,
    make_runner,
    pass_provider_factory,
    run_cli,
    seed_freeze_repo,
    seed_muse_substrate,
)


def _mirror_runner(root: str, *, muse_dirty: bool, git_dirty: bool) -> object:
    return make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok(json.dumps({"dirty": muse_dirty})),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(" M file" if git_dirty else ""),
        }
    )


def test_review_freeze_refuses_then_proceeds_across_a_simulated_muse_commit(tmp_path: Path) -> None:
    root = str(tmp_path.resolve())
    artifact = seed_freeze_repo(tmp_path, config_name="config-muse-git-mirror.yaml")

    # Git already committed (clean); Muse has not — the exact failure this phase closes.
    runner = _mirror_runner(root, muse_dirty=True, git_dirty=False)
    code = run_cli(
        ["review", "--freeze", str(artifact.relative_to(tmp_path))],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 2

    # Operator runs `muse code add -A && muse commit` — simulate the post-commit state.
    runner = _mirror_runner(root, muse_dirty=False, git_dirty=False)
    code = run_cli(
        ["review", "--freeze", str(artifact.relative_to(tmp_path))],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0


def test_governance_sync_refuses_then_proceeds_across_a_simulated_muse_commit(tmp_path: Path) -> None:
    root = str(tmp_path.resolve())
    runner = _mirror_runner(root, muse_dirty=True, git_dirty=False)
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
    seed_muse_substrate(tmp_path)
    (tmp_path / ".muse" / "git-bridge.toml").write_text(
        '[last_export]\n'
        'muse_commit_id = "' + ("a" * 40) + '"\n'
        'git_sha = "' + ("d" * 40) + '"\n'
        '[last_import]\ngit_sha = "' + ("d" * 40) + '"\n',
        encoding="utf-8",
    )

    # Muse still lagging Git — governance-sync must refuse before it does anything else.
    code = run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner)
    assert code == 2

    # After the catch-up muse commit, Muse and Git agree — governance-sync proceeds.
    runner = _mirror_runner(root, muse_dirty=False, git_dirty=False)
    runner.responses.update(
        {
            f"muse -C {root} rev-parse main": ok("a" * 40),
            "git rev-parse origin/main": ok("b" * 40),
            "git rev-parse origin/muse-mirror": ok("c" * 40),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                json.dumps([])
            ),
        }
    )
    code = run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner)
    assert code == 0

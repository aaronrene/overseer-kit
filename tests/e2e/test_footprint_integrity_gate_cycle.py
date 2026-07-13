"""E2E: the footprint self-integrity gate blocks then clears across review + governance-sync
(§KH3.8 e2e tier)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    make_runner,
    ok,
    pass_provider_factory,
    run_cli,
)


def _git_only_runner() -> object:
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
        }
    )


def _init(tmp_path: Path, runner, config_name: str = "config-git-only.yaml") -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / config_name), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )


def test_review_freeze_refuses_then_proceeds_across_a_simulated_sync(tmp_path: Path) -> None:
    runner = _git_only_runner()
    _init(tmp_path, runner)
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    artifact = docs / "FREEZE.md"
    artifact.write_text(
        (FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8"), encoding="utf-8"
    )

    # Simulate this session's own incident: a declared kit-owned file vanishes from disk.
    victim = tmp_path / ".cursor" / "rules" / "governance-sync.mdc"
    saved = victim.read_text(encoding="utf-8")
    victim.unlink()

    code = run_cli(
        ["review", "--freeze", str(artifact.relative_to(tmp_path))],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 2

    # `overseer sync` (simulated by restoring the file) — the documented remediation.
    victim.write_text(saved, encoding="utf-8")
    code = run_cli(
        ["review", "--freeze", str(artifact.relative_to(tmp_path))],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0


def test_governance_sync_refuses_then_proceeds_across_a_simulated_sync(tmp_path: Path) -> None:
    runner = _git_only_runner()
    runner.responses.update(
        {
            "git rev-parse origin/main": ok("a" * 40),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                json.dumps([])
            ),
        }
    )
    _init(tmp_path, runner)

    victim = tmp_path / ".overseer" / "policy" / "tiers.yaml"
    saved = victim.read_text(encoding="utf-8")
    victim.unlink()

    code = run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner)
    assert code == 2

    victim.write_text(saved, encoding="utf-8")
    code = run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner)
    assert code == 0

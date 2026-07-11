"""Data-integrity tests for governance-sync idempotency (§8 data-integrity tier)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from cli.kit_root import kit_root
from tests.support import FIXTURES, ok, make_runner, run_cli, write_config


def _seed(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def _runner(tmp_path: Path):
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )


def test_governance_sync_second_run_aligned(tmp_path: Path) -> None:
    _seed(tmp_path)
    runner = _runner(tmp_path)
    code1 = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code1 == 0
    handover = (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8").replace(
        "deadbeef",
        "cafebabe",
    )
    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text(handover, encoding="utf-8")
    code2 = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code2 == 0


def test_mid_apply_failure_leaves_no_commit(tmp_path: Path) -> None:
    _seed(tmp_path)
    runner = _runner(tmp_path)
    calls = {"n": 0}

    def flaky_write(path: Path, text: str) -> None:
        calls["n"] += 1
        if calls["n"] == 2:
            from cli.atomic import WriteFailure

            raise WriteFailure(path, OSError("simulated"))
        from cli.atomic import atomic_write_text as real

        real(path, text)

    with patch("tools.governance_hygiene.engine.atomic_write_text", side_effect=flaky_write):
        code = run_cli(
            ["governance-sync", "--write"],
            cwd=tmp_path,
            runner=runner,
            kit=kit_root(),
        )
    assert code == 5
    assert not (tmp_path / ".overseer" / "last_governance_sync").exists()

"""Security tests for governance-sync (§8 security tier)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.kit_root import kit_root
from tests.support import FIXTURES, fail, ok, make_runner, run_cli, write_config
from tools.governance_hygiene.engine import _commit_message
from tools.governance_hygiene.types import DriftReport


def test_commit_message_has_no_hardcoded_repo_sha() -> None:
    drift = DriftReport(
        d1_handover_vs_git="drifted",
        d2_anchor_vs_canonical="aligned",
        d3_queue_vs_merged="aligned",
    )
    message = _commit_message("abcdef1234567890", drift, ("vcs-table",), None)
    assert "abcdef1" in message
    assert "deadbeef" not in message
    assert "cdd669f" not in message


def test_gh_auth_failure_fails_closed(tmp_path: Path) -> None:
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
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list": fail("not authenticated", 1),
        }
    )
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    before = handover.read_text(encoding="utf-8")
    code = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 2
    assert handover.read_text(encoding="utf-8") == before


def test_muse_only_never_invokes_git(tmp_path: Path) -> None:
    write_config(tmp_path, "config-muse-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "MUSEHUB-OVERSEER-HANDOVER.md").write_text("# handover\n", encoding="utf-8")
    (docs / "MUSEHUB-ROADMAP.md").write_text("# roadmap\n\n## Build queue\n", encoding="utf-8")
    root = str(tmp_path.resolve())
    runner = make_runner(
        {
            f"muse -C {root} branch --show-current": ok("main"),
            f"muse -C {root} status --porcelain": ok(""),
            f"muse -C {root} rev-parse main": ok('sha256:abc'),
        }
    )
    code = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code in {0, 2}
    assert not any("git " in call[0] for call in runner.calls)
    assert not any("gh " in call[0] for call in runner.calls)

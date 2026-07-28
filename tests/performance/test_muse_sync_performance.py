"""Performance tests: the muse-sync gate adds no extra command invocations (§KH2.8 performance tier)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tests.support import FIXTURES, make_runner, ok, run_cli, seed_muse_substrate
from tools.governance_freshness import GovernanceFreshnessReport


_OK_FRESHNESS = GovernanceFreshnessReport(
    state="ok", message="patched for muse-sync perf", remediation=None
)


def _runner(root: str) -> object:
    return make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": false}'),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
        }
    )


def test_status_call_count_unchanged_by_muse_sync_gate(tmp_path: Path) -> None:
    """§KH2.5: the gate reuses the StatusResult status() already fetched — zero new commands."""
    root = str(tmp_path.resolve())
    runner = _runner(root)
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-muse-git-mirror.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    seed_muse_substrate(tmp_path)

    runner.calls.clear()
    with patch("cli.commands.status.check_governance_freshness", return_value=_OK_FRESHNESS):
        run_cli(["status", "--exit-code"], cwd=tmp_path, runner=runner)

    # Exactly the four calls adapter.status() already made pre-KH2: two muse, two git.
    # (muse status --json succeeds so the --porcelain fallback is never invoked.)
    # GFG freshness is patched out so this test isolates the muse-sync gate only.
    assert len(runner.calls) == 4
    commands = [c[0] for c in runner.calls]
    assert sum(1 for c in commands if "status --json" in c) == 1
    assert sum(1 for c in commands if "status --porcelain" in c and "muse" in c) == 0
    assert sum(1 for c in commands if c == "git status --porcelain") == 1

"""Performance: default status path adds no gh invocation for land closeout
(§PMHF.10 performance)."""

from __future__ import annotations

import time
from pathlib import Path

from tests.support import git_status_runner, land_a_fence_body, land_handover_text, run_cli, seed_land_repo


def test_default_status_path_never_invokes_gh(tmp_path: Path, capsys) -> None:
    # Even when the paste names a PR, status (probe_merged_pr=False) must not call gh.
    seed_land_repo(
        tmp_path,
        handover_text=land_handover_text(
            "cafebabe",
            fence_body=land_a_fence_body(paste_extra="PR #206 open — waiting for merge.\n"),
        ),
    )
    runner = git_status_runner(tip="cafebabe")
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=runner,
        json_mode=True,
    )
    capsys.readouterr()
    assert code == 0
    assert not any(call[0].startswith("gh") for call in runner.calls)


def test_status_with_land_closeout_stays_bounded(tmp_path: Path, capsys) -> None:
    seed_land_repo(tmp_path)
    runner = git_status_runner(tip="cafebabe")
    start = time.monotonic()
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=runner,
        json_mode=True,
    )
    elapsed = time.monotonic() - start
    capsys.readouterr()
    assert code == 0
    assert elapsed < 2.0

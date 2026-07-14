"""Performance — Track O / O3 upgrade-regime dry-run bound (§O2.9 performance)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    make_runner,
    muse_mirror_status_runner,
    muse_status_runner,
    ok,
    run_cli,
    seed_muse_substrate,
)

MAX_SINGLE_DRY_RUN_SECONDS = 15.0


def test_single_dry_run_bounded(tmp_path: Path) -> None:
    seed_muse_substrate(tmp_path)
    assert (
        run_cli(
            [
                "init",
                "--from-config",
                str(FIXTURES / "config-muse-only.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            kit=kit_root(),
            runner=muse_status_runner(tmp_path),
        )
        == 0
    )
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    responses["git remote get-url origin"] = ok("git@github.com:o/r.git")
    runner = make_runner(responses)
    start = time.perf_counter()
    code = run_cli(
        ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--dry-run"],
        cwd=tmp_path,
        kit=kit_root(),
        runner=runner,
    )
    elapsed = time.perf_counter() - start
    assert code == 0
    assert elapsed < MAX_SINGLE_DRY_RUN_SECONDS, f"dry-run too slow: {elapsed:.2f}s"

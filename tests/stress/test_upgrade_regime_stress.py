"""Stress — Track O / O3 upgrade-regime dry-run repeats (§O2.9 stress)."""

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

N = 20
MAX_TOTAL_SECONDS = 60.0


def _init_muse_only(tmp_path: Path) -> None:
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


def test_dry_run_repeated_n_times_bounded(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    responses["git remote get-url origin"] = ok("git@github.com:o/r.git")
    runner = make_runner(responses)
    argv = [
        "upgrade-regime",
        "--from",
        "muse-only",
        "--to",
        "muse+git-mirror",
        "--dry-run",
    ]
    start = time.perf_counter()
    for _ in range(N):
        code = run_cli(argv, cwd=tmp_path, kit=kit_root(), runner=runner)
        assert code == 0
    elapsed = time.perf_counter() - start
    assert elapsed < MAX_TOTAL_SECONDS, f"stress exceeded bound: {elapsed:.2f}s"

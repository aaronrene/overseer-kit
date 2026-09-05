"""Performance — ``ok next`` under 2.0s; no muse/git (§ONS.12 / §NXP.8)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, write_config
from tools.print_next.extract import set_read_at_clock

FIXED_READ_AT = "2026-09-04T12:00:00Z"


def test_ok_next_under_two_seconds(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")

    set_read_at_clock(lambda: FIXED_READ_AT)
    try:
        start = time.perf_counter()
        code = run_cli(["next"], cwd=tmp_path, runner=git_status_runner(), kit=kit_root())
        elapsed = time.perf_counter() - start
        assert code == 0
        assert elapsed < 2.0
    finally:
        set_read_at_clock(None)


def test_ok_next_no_muse_git_subprocess(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    runner = git_status_runner()
    set_read_at_clock(lambda: FIXED_READ_AT)
    try:
        code = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
        assert code == 0
        assert runner.calls == []
    finally:
        set_read_at_clock(None)

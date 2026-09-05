"""Stress — large handover + NXP path edge cases (§ONS.12 / §NXP.8)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import git_status_runner, run_cli, write_config
from tools.print_next.extract import (
    CURRENT_NEXT_HEADING,
    CurrentNextResult,
    extract_current_next,
    format_current_next,
    set_read_at_clock,
)

MARKER = "STRESS-FENCE-BODY-UNIQUE-TOKEN"
PERF_BOUND_S = 2.0
FIXED_READ_AT = "2026-09-04T12:00:00Z"


def test_stress_large_handover_fence_at_end(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    path = docs / "OVERSEER-HANDOVER.md"
    done_rows = "\n".join(f"| **DONE-{i}** | Auto | **DONE** | filler |" for i in range(200))
    filler = ("x" * 1024 + "\n") * (1550)  # ≥1.5 MiB of padding before fence
    body = (
        f"# Handover\n\n## Queue\n\n{done_rows}\n\n{filler}\n"
        f"### Paste-ready prompt — stress\n\n```text\n{MARKER}\nModel: Auto\n```\n"
    )
    path.write_text(body, encoding="utf-8")
    assert path.stat().st_size >= int(1.5 * 1024 * 1024)

    start = time.perf_counter()
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    elapsed = time.perf_counter() - start
    assert isinstance(result, CurrentNextResult)
    assert MARKER in result.fence
    assert "Model: Auto" in result.fence
    assert elapsed < PERF_BOUND_S


def test_stress_long_path_unicode_and_long_fence(tmp_path: Path, capsys) -> None:
    """Deep nested root, unicode/spaces in path, long fence body, long repo name."""
    nested = tmp_path / "deep" / "nest" / "with spaces" / "unicodé-repo"
    nested.mkdir(parents=True)
    write_config(nested, "config-git-only.yaml")
    cfg = (nested / ".overseer" / "config.yaml").read_text(encoding="utf-8")
    long_name = "x" * 80 + "-repo"
    (nested / ".overseer" / "config.yaml").write_text(
        cfg.replace("name: test-git", f"name: {long_name}"),
        encoding="utf-8",
    )
    docs = nested / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    long_body = ("LINE\n" * 500) + "Model: Auto\n"
    (docs / "OVERSEER-HANDOVER.md").write_text(
        f"# H\n\n### Paste-ready prompt\n\n```text\n{long_body}```\n",
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("# R\n", encoding="utf-8")
    set_read_at_clock(lambda: FIXED_READ_AT)
    try:
        code = run_cli(["next"], cwd=nested, runner=git_status_runner(), kit=kit_root())
        out = capsys.readouterr().out
        assert code == 0
        assert CURRENT_NEXT_HEADING in out
        assert long_name in out
        assert nested.resolve().as_posix() in out
        assert out.count("LINE") >= 500
    finally:
        set_read_at_clock(None)


def test_stress_many_lanes_status_advisory(tmp_path: Path) -> None:
    from adapters.config import load_config
    from tools.workspace.board_names import status_board_name_advisory

    write_config(tmp_path, "config-two-lane.yaml")
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    # Two-lane fixture uses bare lane board names → one advisory naming count.
    msg = status_board_name_advisory(config)
    assert msg is not None
    assert "2 lanes non-compliant" in msg
    assert "first:" in msg


def test_stress_format_at_filesystem_root_path() -> None:
    result = CurrentNextResult(path="docs/H.md", lane=None, fence="Model: Auto\n")
    human = format_current_next(
        result,
        repo_name="r",
        repo_root_abs="/",
        read_at=FIXED_READ_AT,
    )
    assert "`/`" in human
    assert human.startswith(CURRENT_NEXT_HEADING)

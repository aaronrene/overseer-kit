"""Integration — ``ok next`` + ``governance-sync --print-next`` (§ONS.12 / §NXP.8)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.commands.next import EXIT_NEXT_MALFORMED
from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, write_config
from tools.print_next.extract import CURRENT_NEXT_HEADING, set_read_at_clock

FIXED_READ_AT = "2026-09-04T12:00:00Z"


def _seed(tmp_path: Path) -> Path:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    handover = docs / "OVERSEER-HANDOVER.md"
    handover.write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    return handover


def _pin_clock():
    set_read_at_clock(lambda: FIXED_READ_AT)


def _unpin_clock():
    set_read_at_clock(None)


def test_ok_next_exit_zero_heading_model(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
    _pin_clock()
    try:
        runner = git_status_runner()
        code = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
        out = capsys.readouterr().out
        assert code == 0
        assert CURRENT_NEXT_HEADING in out
        assert "**Source:**" in out
        assert "Model:" in out
        joined = " ".join(cmd for cmd, _cwd in runner.calls)
        assert "muse" not in joined
        assert "git" not in joined
    finally:
        _unpin_clock()


def test_print_next_synonym_same_stdout(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
    _pin_clock()
    try:
        runner = git_status_runner()
        code_a = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
        out_a = capsys.readouterr().out
        code_b = run_cli(
            ["governance-sync", "--print-next"],
            cwd=tmp_path,
            runner=runner,
            kit=kit_root(),
        )
        out_b = capsys.readouterr().out
        assert code_a == 0
        assert code_b == 0
        assert out_a == out_b
        assert "**Source:**" in out_a
    finally:
        _unpin_clock()


def test_quiet_includes_provenance(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
    _pin_clock()
    try:
        code = run_cli(
            ["--quiet", "next"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        out = capsys.readouterr().out
        assert code == 0
        assert CURRENT_NEXT_HEADING in out
        assert "**Source:**" in out
        assert FIXED_READ_AT in out
    finally:
        _unpin_clock()


def test_json_carries_identity_keys(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
    _pin_clock()
    try:
        code = run_cli(
            ["--json", "next"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            json_mode=True,
        )
        out = capsys.readouterr().out
        assert code == 0
        payload = json.loads(out)
        assert payload["ok"] is True
        assert payload["path"]
        assert "lane" in payload
        assert payload["heading"] == CURRENT_NEXT_HEADING
        assert payload["fence"]
        assert payload["error"] is None
        assert payload["repo_name"] == "test-git"
        assert payload["repo_root"] == tmp_path.resolve().as_posix()
        assert payload["read_at"] == FIXED_READ_AT
    finally:
        _unpin_clock()


def test_lane_flag_two_lane_fixture(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-two-lane.yaml")
    queue = tmp_path / "QUEUE_HANDOVER.md"
    active_dir = tmp_path / "videos" / "_active"
    active_dir.mkdir(parents=True, exist_ok=True)
    body = (
        "# H\n\n### Paste-ready prompt\n\n```text\n"
        "Lane body TOKEN-ACTIVE\nModel: Auto\n```\n"
    )
    queue.write_text(
        "# Q\n\n### Paste-ready prompt\n\n```text\nQueue body\nModel: Auto\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "QUEUE_ROADMAP.md").write_text("# R\n", encoding="utf-8")
    (active_dir / "HANDOVER.md").write_text(body, encoding="utf-8")
    (active_dir / "ROADMAP.md").write_text("# R\n", encoding="utf-8")
    _pin_clock()
    try:
        code = run_cli(
            ["next", "--lane", "active"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        out = capsys.readouterr().out
        assert code == 0
        assert "TOKEN-ACTIVE" in out
        assert "lane `active`" in out
        assert "Queue body" not in out
    finally:
        _unpin_clock()


def test_print_next_write_exclusive(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
    code = run_cli(
        ["governance-sync", "--print-next", "--write"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    err = capsys.readouterr().err
    assert code == 2
    assert "print-next mutually exclusive with --write" in err


def test_print_next_all_lanes_exclusive(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
    code = run_cli(
        ["governance-sync", "--print-next", "--all-lanes"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    err = capsys.readouterr().err
    assert code == 2
    assert "print-next mutually exclusive with --all-lanes" in err


def test_malformed_exit_37(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text("# empty\n", encoding="utf-8")
    code = run_cli(["next"], cwd=tmp_path, runner=git_status_runner(), kit=kit_root())
    assert code == EXIT_NEXT_MALFORMED

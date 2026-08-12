"""Integration — ``ok next`` + ``governance-sync --print-next`` (§ONS.12)."""

from __future__ import annotations

from pathlib import Path

from cli.commands.next import EXIT_NEXT_MALFORMED
from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, write_config
from tools.print_next.extract import CURRENT_NEXT_HEADING


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


def test_ok_next_exit_zero_heading_model(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
    runner = git_status_runner()
    code = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    out = capsys.readouterr().out
    assert code == 0
    assert CURRENT_NEXT_HEADING in out
    assert "Model:" in out
    joined = " ".join(cmd for cmd, _cwd in runner.calls)
    assert "muse" not in joined
    assert "git" not in joined


def test_print_next_synonym_same_stdout(tmp_path: Path, capsys) -> None:
    _seed(tmp_path)
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

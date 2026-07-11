"""Unit tests for checklist replace semantics and exit precedence (§K5.12)."""

from __future__ import annotations

from pathlib import Path

from tests.support import FIXTURES, git_status_runner, run_cli, seed_freeze_repo, write_config
from cli.kit_root import kit_root
from tools.freeze_reviewer.checklist import builtin_checklist, load_checklist_file
from tools.freeze_reviewer.engine import resolve_exit_code
from tools.freeze_reviewer.types import ReviewResult


def test_builtin_checklist_ids() -> None:
    ids = [item.id for item in builtin_checklist()]
    assert ids == ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]


def test_checklist_file_replaces_builtin(tmp_path: Path) -> None:
    items = load_checklist_file(FIXTURES / "checklist-replace.yaml")
    assert [item.id for item in items] == ["X1"]
    builtin_ids = {item.id for item in builtin_checklist()}
    assert not any(item.id in builtin_ids for item in items)


def test_empty_checklist_config_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("checks: []\n", encoding="utf-8")
    import pytest
    from adapters.errors import ConfigError

    with pytest.raises(ConfigError):
        load_checklist_file(path)


def test_checklist_path_escape_exit_four(tmp_path: Path) -> None:
    seed_freeze_repo(tmp_path)
    code = run_cli(
        ["review", "--freeze", "docs/FREEZE.md", "--checklist", "../outside.yaml"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4


def test_exit_precedence() -> None:
    assert resolve_exit_code(ReviewResult(), config_error=True) == 2
    assert resolve_exit_code(ReviewResult(refused=True), refused=True) == 4
    assert resolve_exit_code(ReviewResult(io_error=True)) == 5
    assert resolve_exit_code(ReviewResult(verdict="blocked", escalation="human")) == 8
    assert resolve_exit_code(ReviewResult(verdict="findings")) == 7
    assert resolve_exit_code(ReviewResult(verdict="pass")) == 0

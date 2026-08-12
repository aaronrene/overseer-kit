"""Security — path/lane refusal + honesty greps (§ONS.12 / §ONS.11)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, write_config

REQUIRED_SUBSTRINGS = (
    "## CURRENT NEXT — paste this",
    "ok next",
    "read from disk after write",
    "Session incomplete without it",
    "do not guarantee an accurate open tab",
)

HONESTY = (
    "Host niceties improve odds of tab refresh; they do **not** guarantee an accurate open"
)


def test_config_outside_repo_exit_4(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    outside = tmp_path.parent / "outside-config.yaml"
    outside.write_text(
        (FIXTURES / "config-git-only.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    code = run_cli(
        ["next", "--config", str(outside)],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4


def test_lane_path_escape_exit_2(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    code = run_cli(
        ["next", "--lane", "../x"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 2


def test_git_only_zero_muse_argv(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    runner = git_status_runner()
    code = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert runner.calls == []


def test_skill_rule_required_substrings() -> None:
    root = kit_root()
    skill = (root / "cursor" / "skills" / "print-next" / "SKILL.md").read_text(encoding="utf-8")
    rule = (root / "cursor" / "rules" / "print-next-closeout.mdc").read_text(encoding="utf-8")
    for needle in REQUIRED_SUBSTRINGS:
        assert needle in skill, needle
        assert needle in rule, needle


def test_print_next_doc_honesty_sentence() -> None:
    text = (kit_root() / "docs" / "PRINT-NEXT.md").read_text(encoding="utf-8")
    assert HONESTY in text


def test_stop_hook_fail_closed_false() -> None:
    raw = (kit_root() / "cursor" / "hooks" / "print-next-stop.json").read_text(encoding="utf-8")
    data = json.loads(raw)
    stop = data["hooks"]["stop"][0]
    assert stop["failClosed"] is False


def test_fake_secret_printed_as_data_not_executed(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    token = "sk-test-not-a-real-secret-ons"
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "# H\n\n### Paste-ready prompt\n\n```text\n"
        f"Token {token}\nModel: Auto\n```\n",
        encoding="utf-8",
    )
    runner = git_status_runner()
    code = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    out = capsys.readouterr().out
    assert code == 0
    assert token in out
    for cmd, _cwd in runner.calls:
        assert token not in cmd

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


def test_provenance_leaks_no_secrets(tmp_path: Path, capsys) -> None:
    """§NXP.8 security: provenance emits name/path/lane/timestamp only."""
    from tools.print_next.extract import set_read_at_clock

    write_config(tmp_path, "config-git-only.yaml")
    # Inject a fake token into config to ensure it is not echoed in provenance.
    cfg = tmp_path / ".overseer" / "config.yaml"
    cfg.write_text(
        cfg.read_text(encoding="utf-8") + "\n# secret: sk-config-should-not-leak\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    set_read_at_clock(lambda: "2026-09-04T12:00:00Z")
    try:
        code = run_cli(["next"], cwd=tmp_path, runner=git_status_runner(), kit=kit_root())
        out = capsys.readouterr().out
        assert code == 0
        # Provenance line only — isolate the Source line.
        prov = [ln for ln in out.splitlines() if ln.startswith("**Source:**")][0]
        assert "sk-config-should-not-leak" not in prov
        assert "token" not in prov.lower()
        assert "github.com" not in prov
        assert "remote" not in prov
        assert "test-git" in prov
        assert tmp_path.resolve().as_posix() in prov
        assert "read `" in prov
    finally:
        set_read_at_clock(None)

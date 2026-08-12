"""E2E — write new fence then ``ok next`` prints the new body (§ONS.12)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, seed_git_repo, write_config
from tools.print_next.extract import CURRENT_NEXT_HEADING


NEW_BODY = """You are Auto — NEW FENCE BODY TOKEN abc123.

Model: Auto
"""


def test_e2e_new_fence_then_idempotent(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    seed_git_repo(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    handover = docs / "OVERSEER-HANDOVER.md"
    handover.write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")

    runner = git_status_runner(branch="feat/ons-operator-next-surfacing")
    code1 = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    out1 = capsys.readouterr().out
    assert code1 == 0
    assert "ONS fixture" in out1
    assert "NEW FENCE BODY TOKEN" not in out1

    handover.write_text(
        "# Handover\n\n### Paste-ready prompt — new\n\n```text\n"
        + NEW_BODY
        + "```\n",
        encoding="utf-8",
    )

    code2 = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    out2 = capsys.readouterr().out
    assert code2 == 0
    assert CURRENT_NEXT_HEADING in out2
    assert "NEW FENCE BODY TOKEN abc123" in out2
    assert "ONS fixture" not in out2

    code3 = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    out3 = capsys.readouterr().out
    assert code3 == 0
    assert out3 == out2

    # main tip fixture path unused; ensure we never checked out main via runner.
    assert all("checkout" not in cmd for cmd, _ in runner.calls)

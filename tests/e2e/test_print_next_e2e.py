"""E2E — write new fence then ``ok next`` prints the new body (§ONS.12 / §NXP.8)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    git_status_runner,
    run_cli,
    seed_git_repo,
    seed_governance_freshness,
    write_config,
)
from tools.print_next.extract import CURRENT_NEXT_HEADING, set_read_at_clock
from tools.workspace.board_names import expected_handover_basename

NEW_BODY = """You are Auto — NEW FENCE BODY TOKEN abc123.

Model: Auto
"""

FIXED_READ_AT = "2026-09-04T12:00:00Z"


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

    set_read_at_clock(lambda: FIXED_READ_AT)
    try:
        runner = git_status_runner(branch="feat/ons-operator-next-surfacing")
        code1 = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
        out1 = capsys.readouterr().out
        assert code1 == 0
        assert "ONS fixture" in out1
        assert "NEW FENCE BODY TOKEN" not in out1
        assert "**Source:**" in out1

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
    finally:
        set_read_at_clock(None)


def test_e2e_two_repos_attributable(tmp_path: Path, capsys) -> None:
    """§NXP.8 e2e: two fixture repos in one stream — each block attributable."""
    repo_a = tmp_path / "repo-alpha"
    repo_b = tmp_path / "repo-beta"
    for repo, name in ((repo_a, "alpha"), (repo_b, "beta")):
        write_config(repo, "config-git-only.yaml")
        cfg = (repo / ".overseer" / "config.yaml").read_text(encoding="utf-8")
        (repo / ".overseer" / "config.yaml").write_text(
            cfg.replace("name: test-git", f"name: {name}"),
            encoding="utf-8",
        )
        docs = repo / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "OVERSEER-HANDOVER.md").write_text(
            f"# H\n\n### Paste-ready prompt\n\n```text\n"
            f"Body for {name}\nModel: Auto\n```\n",
            encoding="utf-8",
        )
        (docs / "ROADMAP.md").write_text("# R\n", encoding="utf-8")

    set_read_at_clock(lambda: FIXED_READ_AT)
    try:
        code_a = run_cli(["next"], cwd=repo_a, runner=git_status_runner(), kit=kit_root())
        out_a = capsys.readouterr().out
        code_b = run_cli(["next"], cwd=repo_b, runner=git_status_runner(), kit=kit_root())
        out_b = capsys.readouterr().out
        assert code_a == 0 and code_b == 0
        stream = out_a + out_b
        assert f"`{repo_a.resolve().as_posix()}`" in stream
        assert f"`{repo_b.resolve().as_posix()}`" in stream
        assert "`alpha`" in out_a and "`beta`" in out_b
        assert "Body for alpha" in out_a
        assert "Body for beta" in out_b
    finally:
        set_read_at_clock(None)


def test_e2e_status_exit_code_unchanged_by_advisory(tmp_path: Path, capsys) -> None:
    """§NXP.8 e2e: the N4 advisory must not change ``--exit-code`` (§NXP.6).

    A fully initialized repo with bare board names exits ``0`` on every
    pre-existing condition, so the advisory is the only thing in play. Asserting
    the advisory fires *and* the exit stays ``0`` pins §NXP.6 directly: were the
    advisory folded into the exit-code tiers, this could not remain ``0``.
    """
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=git_status_runner(),
        )
        == 0
    )
    seed_governance_freshness(tmp_path)
    capsys.readouterr()

    code = run_cli(
        ["status", "--exit-code"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    out = capsys.readouterr().out

    # The N4 advisory is genuinely firing on this fixture (bare `OVERSEER-*` names)...
    assert "board naming:" in out
    assert expected_handover_basename("test-git") in out
    # ...and contributes nothing to the exit code (§NXP.6 warn, never a gate).
    assert code == 0

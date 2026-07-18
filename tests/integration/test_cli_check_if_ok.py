"""Integration — ``ok check-if-ok`` scaffolds then delegates to review --freeze."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import git_status_runner, pass_provider_factory, run_cli, write_config
from tools.check_if_ok.scaffold import scaffold_side_check


def test_scaffold_only_creates_artifact(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    code = run_cli(
        ["check-if-ok", "--topic", "integration-spike", "--scaffold-only"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 0
    reviews = list((tmp_path / "docs" / "reviews").glob("*-integration-spike.md"))
    assert len(reviews) == 1
    assert "frozen: true" in reviews[0].read_text(encoding="utf-8")


def test_check_if_ok_runs_same_review_engine(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    result = scaffold_side_check(
        tmp_path,
        topic="wired",
        scope="Integration scope with seven-tier test matrix and file+line citations.",
        today=date(2026, 7, 17),
    )
    code = run_cli(
        ["check-if-ok", "--path", result.rel_path, "--dry-run", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
        json_mode=True,
    )
    # Local checklist may still emit findings; engine must run (not usage/refuse-init).
    assert code in {0, 7, 8}


def test_path_escape_refused(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    code = run_cli(
        ["check-if-ok", "--path", "../outside.md", "--scaffold-only"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4

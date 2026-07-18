"""E2E — scaffold → check-if-ok → equivalent review --freeze on same artifact."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import git_status_runner, pass_provider_factory, run_cli, write_config


def test_scaffold_then_check_and_review_agree(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    assert (
        run_cli(
            ["check-if-ok", "--topic", "e2e-cycle", "--scaffold-only"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 0
    )
    artifact = next((tmp_path / "docs" / "reviews").glob("*-e2e-cycle.md"))
    rel = artifact.relative_to(tmp_path).as_posix()

    code_cio = run_cli(
        ["check-if-ok", "--path", rel, "--dry-run"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    code_review = run_cli(
        ["review", "--freeze", rel, "--dry-run"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code_cio == code_review

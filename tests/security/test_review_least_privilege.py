"""Security tests — review least privilege (§K5.12)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    git_status_runner,
    muse_status_runner,
    pass_provider_factory,
    run_cli,
    seed_freeze_repo,
)

WRITE_VERBS = ("commit", "push", "checkout", "add", "mirror", "realign")


def test_review_never_invokes_write_verbs(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    runner = git_status_runner()
    run_cli(
        ["review", "--freeze", rel, "--dry-run"],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    for command, _cwd in runner.calls:
        for verb in WRITE_VERBS:
            assert verb not in command.lower()


def test_muse_only_review_never_invokes_git(tmp_path: Path) -> None:
    from tests.support import write_config

    write_config(tmp_path, "config-muse-only.yaml")
    artifact = tmp_path / "docs" / "FREEZE.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text((FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8"), encoding="utf-8")
    runner = muse_status_runner(tmp_path)
    run_cli(
        ["review", "--freeze", artifact.relative_to(tmp_path).as_posix()],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert all("git " not in call[0] for call in runner.calls)


def test_traversal_refused(tmp_path: Path) -> None:
    seed_freeze_repo(tmp_path)
    code = run_cli(
        ["review", "--freeze", "../../etc/passwd"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4

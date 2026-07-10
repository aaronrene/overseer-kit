"""Security tests — CLI least privilege (read-only VCS)."""

from __future__ import annotations

from pathlib import Path

from tests.support import git_status_runner, muse_status_runner, run_cli

WRITE_VERBS = ("commit", "push", "checkout", "add", "mirror", "realign")


def test_init_sync_status_never_invoke_write_verbs(tmp_path: Path) -> None:
    runner = git_status_runner()
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path, runner=runner)
    run_cli(["sync", "-y"], cwd=tmp_path, runner=runner)
    run_cli(["status"], cwd=tmp_path, runner=runner)
    for command, _cwd in runner.calls:
        for verb in WRITE_VERBS:
            assert verb not in command.lower()


def test_muse_only_status_never_invokes_git(tmp_path: Path) -> None:
    from tests.support import FIXTURES

    runner = muse_status_runner(tmp_path)
    run_cli(
        ["init", "--from-config", str(FIXTURES / "config-muse-only.yaml"), "--non-interactive"],
        cwd=tmp_path,
        runner=runner,
    )
    run_cli(["status"], cwd=tmp_path, runner=runner)
    assert all("git " not in call[0] for call in runner.calls)

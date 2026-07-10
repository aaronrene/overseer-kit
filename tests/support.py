"""Test helpers (not pytest fixtures)."""

from __future__ import annotations

import os
from pathlib import Path

from adapters.config import OverseerConfig, load_config
from adapters.factory import create_adapter
from adapters.runner import CommandResult, RecordingRunner

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def write_config(repo_root: Path, name: str) -> Path:
    src = FIXTURES / name
    dest = repo_root / ".overseer" / "config.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def load_fixture_config(repo_root: Path, name: str) -> OverseerConfig:
    return load_config(write_config(repo_root, name))


def ok(stdout: str = "") -> CommandResult:
    return CommandResult(stdout=stdout, stderr="", exit_code=0)


def fail(stderr: str = "error", code: int = 1) -> CommandResult:
    return CommandResult(stdout="", stderr=stderr, exit_code=code)


def make_runner(responses: dict[str, CommandResult]) -> RecordingRunner:
    return RecordingRunner(responses=responses, calls=[])


def adapter_for(config: OverseerConfig, repo_root: Path, runner: RecordingRunner):
    return create_adapter(config, repo_root, runner=runner)


def git_status_runner(branch: str = "main", dirty: bool = False) -> RecordingRunner:
    """Recording runner with git-only ``status()`` responses."""
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok(branch),
            "git status --porcelain": ok(dirty_out),
        }
    )


def muse_status_runner(
    repo_root: Path,
    branch: str = "main",
    dirty: bool = False,
) -> RecordingRunner:
    """Recording runner with muse-only ``status()`` responses."""
    root = str(repo_root.resolve())
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            f"muse -C {root} branch --show-current": ok(branch),
            f"muse -C {root} status --porcelain": ok(dirty_out),
        }
    )


def muse_mirror_status_runner(
    repo_root: Path,
    branch: str = "main",
    dirty: bool = False,
) -> RecordingRunner:
    """Recording runner with muse+git-mirror ``status()`` responses."""
    root = str(repo_root.resolve())
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            f"muse -C {root} branch --show-current": ok(branch),
            f"muse -C {root} status --porcelain": ok(dirty_out),
            "git rev-parse --abbrev-ref HEAD": ok(branch),
            "git status --porcelain": ok(dirty_out),
        }
    )


def run_cli(
    argv: list[str],
    *,
    cwd: Path,
    runner: RecordingRunner | None = None,
    kit: Path | None = None,
) -> int:
    """Invoke ``cli.main`` with an injected runner and working directory."""
    from cli.context import CliContext
    from cli.main import main
    from cli.output import OutputContext

    old_cwd = Path.cwd()
    os.chdir(cwd)
    try:
        ctx = CliContext.create(
            runner=runner or make_runner({}),
            cwd=cwd,
            kit=kit,
            output=OutputContext(),
        )
        return main(argv, ctx=ctx)
    finally:
        os.chdir(old_cwd)


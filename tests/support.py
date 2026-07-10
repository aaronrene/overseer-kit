"""Test helpers (not pytest fixtures)."""

from __future__ import annotations

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

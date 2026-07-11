"""Test helpers (not pytest fixtures)."""

from __future__ import annotations

import os
from pathlib import Path

from adapters.config import OverseerConfig, load_config
from adapters.factory import create_adapter
from adapters.runner import CommandResult, RecordingRunner

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PILOT = FIXTURES / "pilot"


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
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok(branch),
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
    review_provider_factory=None,
    json_mode: bool = False,
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
            output=OutputContext(json_mode=json_mode),
            review_provider_factory=review_provider_factory,
        )
        return main(argv, ctx=ctx)
    finally:
        os.chdir(old_cwd)


def seed_freeze_repo(repo_root: Path, *, config_name: str = "config-git-only.yaml") -> Path:
    """Write config and copy a freeze artifact fixture into a temp repo."""
    write_config(repo_root, config_name)
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    artifact = docs / "FREEZE.md"
    artifact.write_text((FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8"), encoding="utf-8")
    return artifact


def pass_provider_factory():
    """Factory returning a provider that always passes."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(scripted_findings=[])

    return _factory


def findings_provider_factory(findings):
    """Factory returning a provider with scripted findings."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(scripted_findings=list(findings))

    return _factory


def unreachable_provider_factory(cause: str = "offline"):
    """Factory returning an unreachable local provider."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(force_unreachable=True, unreachable_cause=cause)

    return _factory


def seed_pilot_tree(
    repo_root: Path,
    *,
    handover_rel: str,
    handover_text: str = "# Hand preserved handover\n",
    roadmap_rel: str | None = None,
    roadmap_text: str | None = None,
    extra_cursor_rules: dict[str, str] | None = None,
) -> None:
    """Create a pre-existing living-doc layout for migrate fixtures."""
    hand = repo_root / handover_rel
    hand.parent.mkdir(parents=True, exist_ok=True)
    hand.write_text(handover_text, encoding="utf-8")
    if roadmap_rel is not None:
        road = repo_root / roadmap_rel
        road.parent.mkdir(parents=True, exist_ok=True)
        road.write_text(roadmap_text or "# Hand preserved roadmap\n", encoding="utf-8")
    if extra_cursor_rules:
        rules = repo_root / ".cursor" / "rules"
        rules.mkdir(parents=True, exist_ok=True)
        for name, text in extra_cursor_rules.items():
            (rules / name).write_text(text, encoding="utf-8")


def lock_origins(repo_root: Path) -> dict[str, str]:
    """Return path → origin map from ``version.lock``."""
    from cli.version_lock import entry_origin, read_version_lock

    lock = read_version_lock(repo_root / ".overseer" / "version.lock")
    return {e.path: entry_origin(e) for e in lock.footprint}


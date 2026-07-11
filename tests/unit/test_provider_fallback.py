"""Unit tests for provider fallback (§K5.8)."""

from __future__ import annotations

from pathlib import Path

from tests.support import FIXTURES, git_status_runner, run_cli, seed_freeze_repo, unreachable_provider_factory, write_config
from cli.kit_root import kit_root


def test_unreachable_provider_human_fallback(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    code = run_cli(
        ["review", "--freeze", str(artifact.relative_to(tmp_path)), "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=unreachable_provider_factory("offline"),
        json_mode=True,
    )
    assert code == 8


def test_unreachable_never_passes(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    code = run_cli(
        ["review", "--freeze", str(artifact.relative_to(tmp_path))],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=unreachable_provider_factory(),
    )
    assert code != 0

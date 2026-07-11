"""Integration tests for review --freeze across regimes (§K5.12)."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
import yaml

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    findings_provider_factory,
    git_status_runner,
    muse_mirror_status_runner,
    muse_status_runner,
    pass_provider_factory,
    run_cli,
    seed_freeze_repo,
    write_config,
)
from tools.freeze_reviewer.types import Finding


@pytest.mark.parametrize(
    ("fixture", "runner_factory"),
    [
        ("config-git-only.yaml", lambda p: git_status_runner()),
        ("config-muse-only.yaml", lambda p: muse_status_runner(p)),
        ("config-muse-git-mirror.yaml", lambda p: muse_mirror_status_runner(p)),
    ],
)
def test_review_freeze_per_regime(tmp_path: Path, fixture: str, runner_factory) -> None:
    artifact = seed_freeze_repo(tmp_path, config_name=fixture)
    rel = artifact.relative_to(tmp_path).as_posix()
    findings = [
        Finding(
            check="C1",
            severity="MAJOR",
            category="completeness",
            path=rel,
            line=1,
            message="test finding",
        ).with_citation()
    ]
    code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=runner_factory(tmp_path),
        kit=kit_root(),
        review_provider_factory=findings_provider_factory(findings),
        json_mode=True,
    )
    assert code == 7


def test_enabled_false_refuses(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["freeze_contract"]["enabled"] = False
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    code = run_cli(
        ["review", "--freeze", artifact.relative_to(tmp_path).as_posix()],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 4


def test_path_escape_refused(tmp_path: Path) -> None:
    seed_freeze_repo(tmp_path)
    code = run_cli(
        ["review", "--freeze", "../outside.md"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4


def test_legacy_config_string_reviews(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    code = run_cli(
        ["review", "--freeze", artifact.relative_to(tmp_path).as_posix(), "--dry-run"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0


def test_dry_run_writes_zero_bytes(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    before = artifact.read_bytes()
    code = run_cli(
        ["review", "--freeze", artifact.relative_to(tmp_path).as_posix(), "--dry-run"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0
    assert artifact.read_bytes() == before


def test_mode_human_skips_provider(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    provider = pass_provider_factory()
    called = {"n": 0}
    original = provider

    def counting_factory(name: str):
        p = original(name)
        real_review = p.review

        def wrapped(**kwargs):
            called["n"] += 1
            return real_review(**kwargs)

        p.review = wrapped  # type: ignore[method-assign]
        return p

    code = run_cli(
        ["review", "--freeze", artifact.relative_to(tmp_path).as_posix(), "--mode", "human", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=counting_factory,
        json_mode=True,
    )
    assert code == 8
    assert called["n"] == 0

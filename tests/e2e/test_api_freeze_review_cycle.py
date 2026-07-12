"""E2E cycle for headless API freeze review (K11)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FakeHttpTransport,
    api_provider_factory,
    git_status_runner,
    run_cli,
    seed_freeze_repo,
)


def test_api_freeze_review_cycle_dry_run_then_stamp(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    transport = FakeHttpTransport(review_body=json.dumps({"findings": []}).encode("utf-8"))

    dry_code = run_cli(
        ["review", "--freeze", rel, "--dry-run", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
        json_mode=True,
    )
    assert dry_code == 0
    before = artifact.read_bytes()

    pass_code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
        json_mode=True,
    )
    assert pass_code == 0
    after_first = artifact.read_bytes()
    assert after_first != before

    second_code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
        json_mode=True,
    )
    assert second_code == 0
    assert artifact.read_bytes() == after_first

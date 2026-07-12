"""Integration tests for headless API freeze review (K11)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FakeHttpTransport,
    api_provider_factory,
    api_unreachable_provider_factory,
    git_status_runner,
    run_cli,
    seed_freeze_repo,
    write_config,
)


def test_api_provider_pass_via_fake_transport(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    transport = FakeHttpTransport(review_body=json.dumps({"findings": []}).encode("utf-8"))
    code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
        json_mode=True,
    )
    assert code == 0
    assert any(call["method"] == "POST" and "/review" in call["url"] for call in transport.calls)


def test_api_provider_findings_exit_7(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    review_body = json.dumps(
        {
            "findings": [
                {
                    "check": "C3",
                    "severity": "MAJOR",
                    "category": "consistency",
                    "path": rel,
                    "line": 1,
                    "message": "Inconsistent exit table.",
                }
            ]
        }
    ).encode("utf-8")
    transport = FakeHttpTransport(review_body=review_body)
    code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
        json_mode=True,
    )
    assert code == 7


def test_api_unreachable_human_escalation(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_unreachable_provider_factory(),
        json_mode=True,
    )
    assert code == 8


def test_api_review_failure_escalates_human(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    transport = FakeHttpTransport(fail_review=True)
    code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
        json_mode=True,
    )
    assert code == 8

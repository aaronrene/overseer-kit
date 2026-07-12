"""Unit tests for K11 headless API freeze provider."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli.kit_root import kit_root
from tools.freeze_reviewer.providers.api_client import ReviewApiClient
from tools.freeze_reviewer.providers.api_prompt import (
    ARTIFACT_BEGIN,
    ARTIFACT_END,
    build_delimited_artifact,
    build_review_request_body,
)
from tools.freeze_reviewer.providers.api_response import ProviderReviewError, parse_review_response
from tools.freeze_reviewer.providers.model_hint import resolve_model_hint
from tools.freeze_reviewer.types import ChecklistItem, ReviewerSettings
from tests.support import FakeHttpTransport


def test_missing_api_key_unreachable(monkeypatch) -> None:
    monkeypatch.delenv("OVERSEER_REVIEW_API_KEY", raising=False)
    monkeypatch.delenv("OVERSEER_REVIEW_API_URL", raising=False)
    ok, cause = ReviewApiClient().reachable()
    assert ok is False
    assert cause == "missing API credentials"


def test_missing_api_url_unreachable(monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "test-key")
    monkeypatch.delenv("OVERSEER_REVIEW_API_URL", raising=False)
    ok, cause = ReviewApiClient().reachable()
    assert ok is False
    assert cause == "missing API base URL"


def test_health_probe_success(monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "test-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    transport = FakeHttpTransport()
    ok, cause = ReviewApiClient(transport=transport).reachable()
    assert ok is True
    assert cause is None
    assert transport.calls[0]["method"] == "GET"
    assert transport.calls[0]["url"].endswith("/health")
    assert "artifact" not in (transport.calls[0]["body"] or b"").decode("utf-8", errors="ignore").lower()


def test_model_hint_resolution() -> None:
    hint = resolve_model_hint("thinking-high", kit_root=kit_root())
    assert "thinking" in hint.lower() or "opus" in hint.lower()


def test_delimited_artifact_wraps_data() -> None:
    wrapped = build_delimited_artifact("phase: K1")
    assert ARTIFACT_BEGIN in wrapped
    assert ARTIFACT_END in wrapped
    assert "phase: K1" in wrapped


def test_review_request_includes_checklist() -> None:
    body = build_review_request_body(
        artifact_text="frozen: true",
        artifact_path="docs/FREEZE.md",
        checklist=[ChecklistItem("C1", "Ground-truth edge", "MAJOR")],
        model_label="thinking-high",
        model_hint="extended thinking",
    )
    assert body["schema_version"] == 1
    assert body["checklist"][0]["id"] == "C1"
    assert ARTIFACT_BEGIN in body["artifact_text"]


def test_parse_valid_findings() -> None:
    payload = json.dumps(
        {
            "findings": [
                {
                    "check": "C2",
                    "severity": "MAJOR",
                    "category": "completeness",
                    "path": "docs/FREEZE.md",
                    "line": 3,
                    "message": "Missing matrix.",
                }
            ]
        }
    ).encode("utf-8")
    findings = parse_review_response(payload, default_path="docs/FREEZE.md")
    assert len(findings) == 1
    assert findings[0].citation == "docs/FREEZE.md:3"


def test_parse_invalid_json_raises() -> None:
    with pytest.raises(ProviderReviewError):
        parse_review_response(b"not-json", default_path="docs/FREEZE.md")


def test_review_api_non_2xx_raises(monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "test-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    transport = FakeHttpTransport(review_status=500, review_body=b'{"error":"backend down"}')
    client = ReviewApiClient(transport=transport)
    with pytest.raises(ProviderReviewError, match="status 500"):
        client.review(
            artifact_text="frozen: true",
            artifact_path="docs/FREEZE.md",
            checklist=[ChecklistItem("C1", "Ground-truth edge", "MAJOR")],
            reviewer=ReviewerSettings(
                mode="agent",
                model="thinking-high",
                provider="api",
                fallback="human",
            ),
        )

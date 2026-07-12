"""Performance bounds for API freeze review (K11)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FakeHttpTransport, api_provider_factory, git_status_runner, run_cli, seed_freeze_repo
from tools.freeze_reviewer.providers.api_client import ReviewApiClient
from tools.freeze_reviewer.providers.base import ApiReviewProvider


def test_api_review_completes_within_budget(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    transport = FakeHttpTransport(review_body=json.dumps({"findings": []}).encode("utf-8"))
    provider = ApiReviewProvider(client=ReviewApiClient(transport=transport))
    calls = {"review": 0, "reachable": 0}
    real_review = provider.review
    real_reachable = provider.reachable

    def review_wrap(**kwargs):
        calls["review"] += 1
        return real_review(**kwargs)

    def reachable_wrap():
        calls["reachable"] += 1
        return real_reachable()

    provider.review = review_wrap  # type: ignore[method-assign]
    provider.reachable = reachable_wrap  # type: ignore[method-assign]

    def factory(_name: str) -> ApiReviewProvider:
        return provider

    start = time.monotonic()
    code = run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=factory,
    )
    elapsed = time.monotonic() - start
    assert code == 0
    assert elapsed < 5.0
    assert calls["review"] <= 1
    assert calls["reachable"] <= 1

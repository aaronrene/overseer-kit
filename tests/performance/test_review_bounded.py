"""Performance bounds for freeze review (§K5.12)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import git_status_runner, pass_provider_factory, run_cli, seed_freeze_repo
from tools.freeze_reviewer.providers.base import LocalReviewProvider


def test_review_completes_within_budget(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    provider = LocalReviewProvider(scripted_findings=[])
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

    def factory(_name: str) -> LocalReviewProvider:
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

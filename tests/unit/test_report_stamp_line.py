"""Unit tests for human report stamp lines (K5b-r F5)."""

from __future__ import annotations

from tools.freeze_reviewer.report import render_human_report
from tools.freeze_reviewer.types import ReviewResult, ReviewStamp


def test_idempotent_pass_stamp_line() -> None:
    result = ReviewResult(
        verdict="pass",
        stamp=ReviewStamp(
            reviewed_at="2026-07-10T00:00:00Z",
            verdict="pass",
            reviewer_mode="agent",
            reviewer_model="thinking-high",
            reviewer_provider="local",
            kit_version="0.1.0",
            artifact_digest="sha256:" + ("a" * 64),
        ),
        stamp_written=False,
        dry_run=False,
        no_stamp=False,
    )
    text = render_human_report(freeze_path="docs/x.md", result=result)
    assert "Stamp: (unchanged — idempotent)" in text
    assert "verdict != pass" not in text

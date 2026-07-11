"""Unit tests for review stamp behavior (§K5.7)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from cli.atomic import WriteFailure
from tests.support import FIXTURES
from tools.freeze_reviewer.artifact import parse_artifact
from tools.freeze_reviewer.stamp import build_stamp, reference_digest, render_stamped_text, write_stamp
from tools.freeze_reviewer.types import ReviewerSettings


def test_markdown_fence_gets_review_stamp(tmp_path: Path) -> None:
    path = tmp_path / "docs" / "freeze.md"
    path.parent.mkdir(parents=True)
    path.write_text((FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8"), encoding="utf-8")
    parsed = parse_artifact(path, rel_path="docs/freeze.md")
    stamp = build_stamp(parsed, reviewer=ReviewerSettings("agent", "thinking-high", "local", "human"), kit_version="0.1.0")
    text = render_stamped_text(parsed, stamp)
    assert "review_stamp:" in text
    assert "| Round |" not in text or "review_stamp:" in text


def test_yaml_whole_file_gets_top_level_stamp(tmp_path: Path) -> None:
    path = tmp_path / "freeze.yaml"
    path.write_text((FIXTURES / "freeze-artifact.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    parsed = parse_artifact(path, rel_path="freeze.yaml")
    stamp = build_stamp(parsed, reviewer=ReviewerSettings("agent", "thinking-high", "local", "human"), kit_version="0.1.0")
    text = render_stamped_text(parsed, stamp)
    assert text.startswith("phase:")
    assert "review_stamp:" in text


def test_operator_forced_markdown_appends_marker(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text("# Notes only\n", encoding="utf-8")
    parsed = parse_artifact(path, rel_path="notes.md")
    stamp = build_stamp(parsed, reviewer=ReviewerSettings("agent", "thinking-high", "local", "human"), kit_version="0.1.0")
    text = render_stamped_text(parsed, stamp)
    assert "<!-- overseer:review-stamp -->" in text


def test_idempotent_same_digest_noop(tmp_path: Path) -> None:
    path = tmp_path / "freeze.yaml"
    path.write_text((FIXTURES / "freeze-artifact.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    parsed = parse_artifact(path, rel_path="freeze.yaml")
    reviewer = ReviewerSettings("agent", "thinking-high", "local", "human")
    stamp = build_stamp(parsed, reviewer=reviewer, kit_version="0.1.0")
    write_stamp(path, parsed, stamp)
    first = path.read_bytes()
    reparsed = parse_artifact(path, rel_path="freeze.yaml")
    stamp2 = build_stamp(reparsed, reviewer=reviewer, kit_version="0.1.0")
    assert write_stamp(path, reparsed, stamp2) is False
    assert path.read_bytes() == first


def test_atomic_failure_preserves_bytes(tmp_path: Path) -> None:
    path = tmp_path / "freeze.yaml"
    original = (FIXTURES / "freeze-artifact.yaml").read_text(encoding="utf-8")
    path.write_text(original, encoding="utf-8")
    parsed = parse_artifact(path, rel_path="freeze.yaml")
    stamp = build_stamp(parsed, reviewer=ReviewerSettings("agent", "thinking-high", "local", "human"), kit_version="0.1.0")
    with patch("tools.freeze_reviewer.stamp.atomic_write_text", side_effect=WriteFailure(path, OSError("disk"))):
        with pytest.raises(WriteFailure):
            write_stamp(path, parsed, stamp)
    assert path.read_text(encoding="utf-8") == original


def test_digest_uses_bom_strip_and_lf(tmp_path: Path) -> None:
    path = tmp_path / "freeze.yaml"
    path.write_bytes(b"\xef\xbb\xbfphase: K\r\noutputs:\r\n  - id: a\r\n    path: docs/a.md\r\n    frozen: true\r\n")
    parsed = parse_artifact(path, rel_path="freeze.yaml")
    digest = reference_digest(parsed)
    assert digest.startswith("sha256:")

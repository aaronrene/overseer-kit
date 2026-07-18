"""Unit tests — Check-if-OK scaffold + footprint membership."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from cli.footprint import resolve_footprint
from tools.check_if_ok.scaffold import (
    render_side_check_markdown,
    resolve_artifact_path,
    scaffold_side_check,
    slugify_topic,
)


def test_slugify_topic_normalizes() -> None:
    assert slugify_topic("  My Side Research!! ") == "my-side-research"
    assert slugify_topic("") == "side-check"


def test_render_includes_frozen_true_and_seven_tiers() -> None:
    body = render_side_check_markdown(
        topic="demo",
        phase_id="check-if-ok-demo",
        scope="Scope text with seven-tier coverage.",
        output_path="docs/reviews/2026-07-17-demo.md",
        date_stamp="2026-07-17",
    )
    assert "frozen: true" in body
    assert "phase: check-if-ok-demo" in body
    assert "seven-tier" in body.lower() or "Seven tiers" in body or "| unit |" in body
    assert "file+line" in body


def test_resolve_artifact_path_default_under_reviews(tmp_path: Path) -> None:
    target = resolve_artifact_path(
        tmp_path,
        topic="spike",
        today=date(2026, 7, 17),
    )
    assert target == tmp_path / "docs" / "reviews" / "2026-07-17-spike.md"


def test_scaffold_creates_then_reuses(tmp_path: Path) -> None:
    first = scaffold_side_check(
        tmp_path,
        topic="spike",
        scope="Unit scope.",
        today=date(2026, 7, 17),
    )
    assert first.created is True
    assert first.path.is_file()
    assert "frozen: true" in first.path.read_text(encoding="utf-8")

    second = scaffold_side_check(
        tmp_path,
        topic="spike",
        today=date(2026, 7, 17),
    )
    assert second.created is False
    assert second.rel_path == first.rel_path


def test_scaffold_path_escape_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="path-escape"):
        scaffold_side_check(tmp_path, path="../outside.md")


def test_footprint_includes_check_if_ok_skill_and_rule(git_only_config) -> None:
    dests = {f.destination for f in resolve_footprint(git_only_config)}
    assert ".cursor/skills/check-if-ok/SKILL.md" in dests
    assert ".cursor/skills/check-if-ok/SIDE-CHECK-TEMPLATE.md" in dests
    assert ".cursor/rules/check-if-ok-thinking.mdc" in dests


def test_skill_documents_same_engine_as_review(git_only_config) -> None:
    files = {f.destination: f.text for f in resolve_footprint(git_only_config)}
    skill = files[".cursor/skills/check-if-ok/SKILL.md"]
    assert "ok review --freeze" in skill
    assert "ok check-if-ok" in skill
    assert "build-verification-review" in skill
    assert "docs.lanes" in skill

"""Stress — many sequential Check-if-OK scaffolds stay isolated."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tools.check_if_ok.scaffold import scaffold_side_check


def test_many_topics_do_not_collide(tmp_path: Path) -> None:
    paths = set()
    for i in range(40):
        result = scaffold_side_check(
            tmp_path,
            topic=f"topic-{i}",
            today=date(2026, 7, 17),
        )
        assert result.created is True
        paths.add(result.rel_path)
    assert len(paths) == 40

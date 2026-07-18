"""Data-integrity — reuse must not clobber an existing side-check body."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tools.check_ok.scaffold import scaffold_side_check


def test_reuse_preserves_operator_edits(tmp_path: Path) -> None:
    first = scaffold_side_check(
        tmp_path,
        topic="preserve",
        scope="original scope",
        today=date(2026, 7, 17),
    )
    marker = "OPERATOR-EDIT-MARKER"
    first.path.write_text(first.path.read_text(encoding="utf-8") + f"\n{marker}\n", encoding="utf-8")

    second = scaffold_side_check(
        tmp_path,
        topic="preserve",
        scope="should not overwrite",
        today=date(2026, 7, 17),
    )
    assert second.created is False
    assert marker in second.path.read_text(encoding="utf-8")

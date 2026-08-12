"""Unit — print_next extract + format (§ONS.12)."""

from __future__ import annotations

from pathlib import Path

from tools.governance_hygiene.next_regen import extract_paste_fence_body
from tools.print_next.extract import (
    CURRENT_NEXT_HEADING,
    CurrentNextError,
    CurrentNextResult,
    extract_current_next,
    format_current_next,
)

VALID = """# Handover

### Paste-ready prompt — demo

```text
Phase demo.
Model: Auto
```
"""


def _write(tmp: Path, text: str) -> Path:
    path = tmp / "docs" / "OVERSEER-HANDOVER.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_handover_heading_and_body(tmp_path: Path) -> None:
    path = _write(tmp_path, VALID)
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    assert isinstance(result, CurrentNextResult)
    assert result.heading == CURRENT_NEXT_HEADING
    assert "Model: Auto" in result.fence
    human = format_current_next(result)
    assert human.startswith(CURRENT_NEXT_HEADING + "\n\n```text\n")
    assert human.endswith("```\n")


def test_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    result = extract_current_next(
        missing, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None
    )
    assert isinstance(result, CurrentNextError)
    assert result.reason == "handover_missing"


def test_heading_missing_even_if_other_fence(tmp_path: Path) -> None:
    text = "# No paste heading\n\n```\nsome fence\nModel: Auto\n```\n"
    path = _write(tmp_path, text)
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    assert isinstance(result, CurrentNextError)
    assert result.reason == "heading_missing"


def test_fence_missing(tmp_path: Path) -> None:
    text = "### Paste-ready prompt — x\n\nNo fence here.\n"
    path = _write(tmp_path, text)
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    assert isinstance(result, CurrentNextError)
    assert result.reason == "fence_missing"


def test_fence_empty(tmp_path: Path) -> None:
    text = "### Paste-ready prompt — x\n\n```text\n   \n```\n"
    path = _write(tmp_path, text)
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    assert isinstance(result, CurrentNextError)
    assert result.reason == "fence_empty"


def test_model_missing(tmp_path: Path) -> None:
    text = "### Paste-ready prompt — x\n\n```text\nNo model label here.\n```\n"
    path = _write(tmp_path, text)
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    assert isinstance(result, CurrentNextError)
    assert result.reason == "model_missing"


def test_current_next_heading_exact() -> None:
    assert CURRENT_NEXT_HEADING == "## CURRENT NEXT — paste this"


def test_reuses_extract_paste_fence_body(tmp_path: Path) -> None:
    helper = extract_paste_fence_body(VALID)
    assert helper is not None
    path = _write(tmp_path, VALID)
    outcome = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    assert isinstance(outcome, CurrentNextResult)
    assert outcome.fence == helper

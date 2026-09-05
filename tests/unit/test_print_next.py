"""Unit — print_next extract + format (§ONS.12 / §NXP.8)."""

from __future__ import annotations

from pathlib import Path

from tools.governance_hygiene.next_regen import extract_paste_fence_body
from tools.print_next.extract import (
    CURRENT_NEXT_HEADING,
    PROVENANCE_LINE_TEMPLATE,
    PROVENANCE_SEPARATOR,
    CurrentNextError,
    CurrentNextResult,
    extract_current_next,
    format_current_next,
    format_provenance_line,
)

VALID = """# Handover

### Paste-ready prompt — demo

```text
Phase demo.
Model: Auto
```
"""

FIXED_READ_AT = "2026-09-04T12:00:00Z"


def _write(tmp: Path, text: str) -> Path:
    path = tmp / "docs" / "OVERSEER-HANDOVER.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _format(result: CurrentNextResult, **kwargs) -> str:
    defaults = {
        "repo_name": "test-git",
        "repo_root_abs": "/tmp/repo",
        "read_at": FIXED_READ_AT,
    }
    defaults.update(kwargs)
    return format_current_next(result, **defaults)


def test_valid_handover_heading_and_body(tmp_path: Path) -> None:
    path = _write(tmp_path, VALID)
    result = extract_current_next(path, repo_relative_path="docs/OVERSEER-HANDOVER.md", lane=None)
    assert isinstance(result, CurrentNextResult)
    assert result.heading == CURRENT_NEXT_HEADING
    assert "Model: Auto" in result.fence
    human = _format(result)
    # §NXP.3.1 twelve-step layout: heading, blank, provenance, blank, fence.
    assert human.startswith(CURRENT_NEXT_HEADING + "\n\n")
    lines = human.splitlines(keepends=True)
    assert lines[0] == CURRENT_NEXT_HEADING + "\n"
    assert lines[1] == "\n"
    assert lines[2].startswith("**Source:** ")
    assert lines[3] == "\n"
    assert lines[4] == "```text\n"
    assert human.endswith("```\n")
    assert "```text\nPhase demo.\nModel: Auto\n```\n" in human


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


# --- §NXP.8 unit ---


def test_provenance_template_and_separator() -> None:
    assert PROVENANCE_SEPARATOR == " · "
    assert " · " in PROVENANCE_LINE_TEMPLATE
    assert PROVENANCE_LINE_TEMPLATE == (
        "**Source:** `{repo_name}` · `{repo_root_abs}` · `{doc_rel}` · lane `{lane}` · read `{read_at}`"
    )


def test_provenance_fallbacks_unknown_name_and_dash_lane() -> None:
    line = format_provenance_line(
        repo_name=None,
        repo_root_abs="/abs/root",
        doc_rel="docs/OVERSEER-HANDOVER.md",
        lane=None,
        read_at=FIXED_READ_AT,
    )
    assert line == (
        f"**Source:** `unknown` · `/abs/root` · `docs/OVERSEER-HANDOVER.md` · "
        f"lane `-` · read `{FIXED_READ_AT}`"
    )


def test_read_at_format_second_precision_z() -> None:
    from tools.print_next.extract import utc_read_at
    import re

    stamp = utc_read_at()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", stamp)


def test_twelve_step_layout_byte_order(tmp_path: Path) -> None:
    path = _write(tmp_path, VALID)
    result = extract_current_next(path, repo_relative_path="docs/H.md", lane="product")
    assert isinstance(result, CurrentNextResult)
    human = _format(result, repo_root_abs="/r", read_at=FIXED_READ_AT)
    expected_prov = (
        f"**Source:** `test-git` · `/r` · `docs/H.md` · lane `product` · read `{FIXED_READ_AT}`"
    )
    assert human == (
        f"{CURRENT_NEXT_HEADING}\n\n{expected_prov}\n\n```text\nPhase demo.\nModel: Auto\n```\n"
    )


def test_board_name_violation_reused_not_forked() -> None:
    from tools.workspace.board_names import (
        board_name_violation,
        check_next_unconfigured_advisory,
        status_board_name_advisory,
    )
    import inspect

    # Advisory helpers must call board_name_violation (no forked predicate).
    src = inspect.getsource(check_next_unconfigured_advisory)
    assert "board_name_violation" in src
    src2 = inspect.getsource(status_board_name_advisory)
    assert "board_name_violation" in src2
    assert board_name_violation(
        repo_name="test-git",
        handover_basename="OVERSEER-HANDOVER.md",
        roadmap_basename="ROADMAP.md",
        strict=True,
    )

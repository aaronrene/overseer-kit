"""Unit tests for GS-PASTE NEXT / paste regeneration (§GSP.10 unit)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from tools.governance_hygiene.next_regen import (
    compact_step_id,
    decide_split_emission,
    plan_next_regen,
    render_next_session,
    render_paste_ready,
    select_unambiguous_next_row,
)
from tools.governance_hygiene.patch import _render_next_step_glance
from tools.governance_hygiene.types import QueueRow


def _roadmap(*rows: str) -> str:
    header = (
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
    )
    return header + "\n".join(rows) + "\n"


def test_select_exactly_one_open_row() -> None:
    text = _roadmap(
        "| **Done** | Auto | **DONE** | x |",
        "| **Open** | Auto | **NEXT** | y |",
    )
    row, reason = select_unambiguous_next_row(text)
    assert reason is None
    assert row is not None
    assert "Open" in row.phase_label


def test_select_zero_open_rows() -> None:
    text = _roadmap("| **Done** | Auto | **DONE** | x |")
    row, reason = select_unambiguous_next_row(text)
    assert row is None
    assert reason == "zero_open_rows"


def test_select_multiple_open_rows() -> None:
    text = _roadmap(
        "| **A** | Auto | **TODO** | a |",
        "| **B** | Auto | **WIP** | b |",
    )
    row, reason = select_unambiguous_next_row(text)
    assert row is None
    assert reason == "multiple_open_rows"


def test_select_invalid_model_ambiguous() -> None:
    text = _roadmap("| **Open** | Operator choice | **NEXT** | y |")
    row, reason = select_unambiguous_next_row(text)
    assert row is None
    assert reason == "invalid_model_label"


def test_thinking_to_auto_emit_b_when_freeze_pass(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "PHASE-GS-PASTE-READY-REGEN.md").write_text(
        "# Freeze\n\n```yaml\nphase: GS-PASTE\nreview_stamp:\n  verdict: pass\n```\n",
        encoding="utf-8",
    )
    row = QueueRow(
        phase_label="**GS-PASTE**",
        model="Thinking → Auto",
        status="**NEXT**",
        deliverable="docs/archive/phases/PHASE-GS-PASTE-READY-REGEN.md",
        raw_line="",
    )
    emit_model, reason, is_b = decide_split_emission(row, tmp_path)
    assert reason is None
    assert emit_model == "Auto"
    assert is_b is True


def test_thinking_to_auto_emit_a_without_freeze_pass(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    row = QueueRow(
        phase_label="**GS-PASTE**",
        model="Thinking → Auto",
        status="**NEXT**",
        deliverable="freeze something",
        raw_line="",
    )
    emit_model, reason, is_b = decide_split_emission(row, tmp_path)
    assert reason is None
    assert emit_model == "Thinking"
    assert is_b is False


def test_rendered_next_contains_h3_h5_h6_substrings(tmp_path: Path) -> None:
    config = load_config(
        Path(__file__).resolve().parents[1] / "fixtures" / "config-git-only.yaml"
    )
    roadmap = _roadmap(
        "| **Prior** | Auto | **DONE** | prior work |",
        "| **GS-PASTE-b** | Auto | **NEXT** | regen paste |",
    )
    decision = plan_next_regen(
        roadmap_text=roadmap,
        handover_text="## NEXT SESSION — x\n",
        config=config,
        repo_root=tmp_path,
    )
    assert decision.row is not None
    body = render_next_session(
        decision=decision,
        roadmap_text=roadmap,
        config=config,
        sync_date="2026-07-30",
    )
    assert "**Date:**" in body
    assert "**Current position:**" in body
    assert "**Model:**" in body
    assert "### THE ONE NEXT STEP — **Model:" in body
    assert "| **ID** |" in body
    assert "| **Branch** |" in body
    assert "| **Repo** |" in body
    assert "| **Read first** |" in body
    assert "| **Hard stops** |" in body
    assert "### Paste-ready prompt" not in body

    paste = render_paste_ready(decision=decision, config=config)
    assert "### Paste-ready prompt —" in paste
    assert "Model: Auto" in paste
    assert "Repo:" in paste
    assert "Step:" in paste
    assert "Authority:" in paste
    assert "build-verification-review" in paste


def test_glance_fail_closed_when_open_count_not_one() -> None:
    multi = _roadmap(
        "| **A** | Auto | **TODO** | a |",
        "| **B** | Auto | **WIP** | b |",
    )
    glance = _render_next_step_glance(multi)
    assert "No unambiguous NEXT row — operator authorship required." in glance

    zero = _roadmap("| **A** | Auto | **DONE** | a |")
    assert "No unambiguous NEXT row" in _render_next_step_glance(zero)


def test_compact_step_id_uses_first_segment() -> None:
    assert compact_step_id("**GS-PASTE-b Paste regen**") == "GS-PASTE-b"

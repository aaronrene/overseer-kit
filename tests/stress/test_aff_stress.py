"""Stress tests for AFF probe under large roadmap/ledger (§AFF.14)."""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.aff import (
    AFF_FREEZE_REL,
    aff_body,
    seed_aff_repo,
    write_mechanical_stamp,
)
from tools.adversarial_freeze import build_adversarial_freeze_gate
from tools.governance_hygiene.next_regen import plan_next_regen
from tools.honesty.ledger import append_entry
from tools.honesty.types import LedgerAppendOptions


def test_two_hundred_row_roadmap_aff_probe_bounded(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)

    # large ledger of unrelated entries + one open Auto row
    for i in range(80):
        body = aff_body(
            artifact_digest="sha256:" + (f"{i:064d}"[-64:]),
            round=i + 1,
            actor_session_id=f"adv-{i}",
            phase_id=f"OTHER-{i}",
            frozen_spec=f"docs/other-{i}.md",
        )
        assert (
            append_entry(
                config=config,
                repo_root=repo_root,
                options=LedgerAppendOptions(kind="adversarial_freeze", body=body),
            ).exit_code
            == 0
        )

    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="freeze_review",
            body={
                "actor_role": "verifier",
                "actor_session_id": "frv-1",
                "phase_id": "AFF-b",
                "frozen_spec": AFF_FREEZE_REL,
                "round": 1,
                "gate": "substantive",
                "freeze_verdict": "pass",
                "artifact_digest": digest,
                "reviewer_model": "thinking-high",
            },
        ),
    )

    rows = [
        "# Roadmap",
        "",
        "## Build queue",
        "",
        "| Phase | Model | Status | Deliverable |",
        "| --- | --- | --- | --- |",
    ]
    for i in range(199):
        rows.append(f"| **DONE-{i}** | Auto | **DONE** | docs/done-{i}.md |")
    rows.append(
        f"| **AFF-b** | Auto | **NEXT** | `{AFF_FREEZE_REL}` |"
    )
    roadmap = "\n".join(rows) + "\n"
    handover = "## NEXT SESSION — AFF-b\n\n| | |\n| **ID** | **AFF-b** |\n\n"

    decision = plan_next_regen(
        roadmap_text=roadmap,
        handover_text=handover,
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Thinking"
    assert decision.advisory == "adversarial_freeze_pending"

    gate = build_adversarial_freeze_gate(
        config, repo_root, handover_text=handover, roadmap_text=roadmap
    )
    assert gate.skipped is False
    assert gate.state == "pending"

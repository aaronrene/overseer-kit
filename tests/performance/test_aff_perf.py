"""Performance bounds for Mode E + ok next AFF probe (§AFF.14)."""

from __future__ import annotations

import time

from tests.fixtures.aff import (
    AFF_FREEZE_REL,
    aff_body,
    seed_aff_repo,
    write_mechanical_stamp,
)
from tools.adversarial_freeze import build_adversarial_freeze_gate
from tools.governance_hygiene.next_regen import plan_next_regen
from tools.honesty.ledger import append_entry
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions

_BUDGET_S = 2.0


def test_mode_e_and_next_aff_probe_within_bound(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    body = aff_body(artifact_digest=digest)
    started = time.perf_counter()
    assert (
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="adversarial_freeze", body=body),
        ).exit_code
        == 0
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result.exit_code == 0
    roadmap = (
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        f"| **AFF-a** | Thinking | **NEXT** | `{AFF_FREEZE_REL}` |\n"
    )
    handover = "## NEXT SESSION — AFF-a\n\n| | |\n| **ID** | **AFF-a** |\n\n"
    decision = plan_next_regen(
        roadmap_text=roadmap,
        handover_text=handover,
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Thinking"
    report = build_adversarial_freeze_gate(
        config,
        repo_root,
        handover_text=handover,
        roadmap_text=(
            "# Roadmap\n\n## Build queue\n\n"
            "| Phase | Model | Status | Deliverable |\n"
            "| --- | --- | --- | --- |\n"
            f"| **AFF-b** | Auto | **WIP** | `{AFF_FREEZE_REL}` |\n"
        ),
    )
    assert report.skipped is True or report.ok is True
    elapsed = time.perf_counter() - started
    assert elapsed < _BUDGET_S

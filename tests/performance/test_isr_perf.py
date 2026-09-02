"""Performance bounds for ISR append / Mode D / active-slice probe (§ISR.11)."""

from __future__ import annotations

import time

from tests.fixtures.isr import load_isr_entry, seed_isr_repo
from tools.honesty.ledger import append_entry
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions
from tools.independent_second_reviewer import build_independent_second_reviewer_gate

_BUDGET_S = 2.0


def test_append_mode_d_and_gate_within_bound(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="warn")
    body = load_isr_entry("isr-pass.json")
    started = time.perf_counter()
    assert (
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="independent_second_review", body=body),
        ).exit_code
        == 0
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
        ),
    )
    assert result.exit_code == 0
    report = build_independent_second_reviewer_gate(
        config,
        repo_root,
        handover_text="## NEXT\n| **ID** | **ISR-b** |\n",
        roadmap_text=(
            "| Phase | Model | Status | Deliverable |\n"
            "| --- | --- | --- | --- |\n"
            "| **ISR-b** | Auto | **WIP** | `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md` |\n"
        ),
    )
    assert report.skipped is True or report.ok is True
    elapsed = time.perf_counter() - started
    assert elapsed < _BUDGET_S

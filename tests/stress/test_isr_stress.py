"""Stress tests for ISR match scan (§ISR.11)."""

from __future__ import annotations

from tests.fixtures.isr import load_isr_entry, seed_isr_repo
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import find_matching_independent_second_review


def test_fifty_isr_entries_last_wins_match(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="require")
    for round_num in range(1, 51):
        body = load_isr_entry("isr-pass.json")
        body["round"] = round_num
        body["actor_session_id"] = f"verifier-{round_num}"
        body["producer_session_id"] = f"builder-{round_num}"
        assert (
            append_entry(
                config=config,
                repo_root=repo_root,
                options=LedgerAppendOptions(kind="independent_second_review", body=body),
            ).exit_code
            == 0
        )
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 0

    from tools.honesty.ledger_io import read_ledger_entries
    from cli.paths import confine_path

    entries = read_ledger_entries(confine_path(repo_root, config.honesty.ledger))
    winner = find_matching_independent_second_review(
        entries,
        phase_id="ISR-b",
        frozen_spec=None,
        producer_session=None,
    )
    assert winner is not None
    assert winner["round"] == 50

    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
            producer_session="builder-50",
        ),
    )
    assert result.exit_code == 0
    assert result.json_payload.independent_second_review["matched_entry_hash"] is not None

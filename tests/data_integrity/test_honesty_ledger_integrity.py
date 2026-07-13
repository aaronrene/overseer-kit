"""Data-integrity tests for honesty ledger append."""

from __future__ import annotations

import json

from tests.support import load_honesty_config, load_honesty_entry
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.ledger_io import read_ledger_entries
from tools.honesty.types import LedgerAppendOptions


def test_dual_genesis_entry_atomic(repo_root) -> None:
    config = load_honesty_config(repo_root)
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    assert result.exit_code == 0
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    entries = read_ledger_entries(ledger)
    assert len(entries) == 2
    assert entries[0]["kind"] == "genesis"
    assert entries[1]["kind"] == "verdict"
    assert entries[1]["prev_hash"] == entries[0]["entry_hash"]


def test_verify_idempotent(repo_root) -> None:
    config = load_honesty_config(repo_root)
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    first = verify_ledger_file(config=config, repo_root=repo_root)
    second = verify_ledger_file(config=config, repo_root=repo_root)
    assert first.exit_code == 0
    assert second.exit_code == 0


def test_verify_empty_ledger_zero(repo_root) -> None:
    config = load_honesty_config(repo_root)
    result = verify_ledger_file(config=config, repo_root=repo_root)
    assert result.exit_code == 0

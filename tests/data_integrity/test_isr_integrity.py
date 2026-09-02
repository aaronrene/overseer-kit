"""Data-integrity tests for ISR ledger hashing (§ISR.11)."""

from __future__ import annotations

import pytest

from tests.fixtures.isr import load_isr_entry, seed_isr_repo
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import EntryValidationError, validate_append_body


def test_tamper_producer_session_breaks_verify(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    body = load_isr_entry("isr-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    text = ledger.read_text(encoding="utf-8")
    ledger.write_text(
        text.replace("builder-chat-1", "tampered-builder", 1),
        encoding="utf-8",
    )
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 22


def test_canonical_hash_includes_isr_fields() -> None:
    base = {
        "v": 1,
        "kind": "independent_second_review",
        "actor_session_id": "v1",
        "producer_session_id": "p1",
        "isr_verdict": "pass",
    }
    h1 = compute_entry_hash(base)
    h2 = compute_entry_hash({**base, "isr_verdict": "findings"})
    h3 = compute_entry_hash({**base, "producer_session_id": "p2"})
    assert h1 != h2
    assert h1 != h3


def test_append_does_not_embed_chat_transcript(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    body = load_isr_entry("isr-pass.json")
    body["notes"] = "summary only — no full transcript"
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    )
    ledger_text = (
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ).read_text(encoding="utf-8")
    assert "Human:" not in ledger_text
    assert "```python" not in ledger_text


def test_validate_fail_writes_nothing(repo_root) -> None:
    seed_isr_repo(repo_root)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    before = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    body = load_isr_entry("isr-pass.json")
    body["isr_verdict"] = "nope"
    with pytest.raises(EntryValidationError):
        validate_append_body(kind="independent_second_review", body=body)
    after = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    assert after == before


def test_mode_d_omit_vs_pin_does_not_rewrite_ledger(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="require")
    body = load_isr_entry("isr-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    before = ledger.read_text(encoding="utf-8")
    run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
        ),
    )
    run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
            producer_session="builder-chat-1",
        ),
    )
    assert ledger.read_text(encoding="utf-8") == before

"""Integration tests for honesty ledger append and status."""

from __future__ import annotations

import json

from tests.support import honesty_artifact_hash, load_honesty_config, load_honesty_entry
from tools.honesty.ledger import append_entry, show_entries, verify_ledger_file
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions


def test_append_verify_round_trip(repo_root) -> None:
    config = load_honesty_config(repo_root)
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    code = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    ).exit_code
    assert code == 0
    verify = verify_ledger_file(config=config, repo_root=repo_root)
    assert verify.exit_code == 0


def test_first_append_auto_genesis(repo_root) -> None:
    config = load_honesty_config(repo_root)
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    lines = ledger.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["kind"] == "genesis"


def test_missing_ledger_status_20(repo_root) -> None:
    config = load_honesty_config(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 20


def test_co_requirement_pass(repo_root) -> None:
    config = load_honesty_config(repo_root)
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="handoff", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 0
    assert result.json_payload.matched_verdict_hash is not None


def test_ledger_show_missing_empty(repo_root) -> None:
    config = load_honesty_config(repo_root)
    result = show_entries(config=config, repo_root=repo_root, last_n=5)
    assert result.exit_code == 0
    assert result.stdout_lines == []

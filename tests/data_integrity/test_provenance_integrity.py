"""Data-integrity tests for Track P / P1 provenance (§P0.8)."""

from __future__ import annotations

import json

from tests.support import (
    attach_signed_provenance,
    generate_ed25519_keypair,
    load_honesty_config,
    load_honesty_entry,
    sign_append_body,
)
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.genesis import build_genesis_entry
from tools.honesty.ledger import append_entry, verify_ledger_file, verify_chain
from tools.honesty.ledger_io import read_ledger_entries, serialize_entry
from tools.honesty.types import LedgerAppendOptions


def _append_signed_verdict(repo_root) -> tuple[dict, dict]:
    genesis = build_genesis_entry(ts="2026-01-01T00:00:00Z")
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(serialize_entry(genesis), encoding="utf-8")
    config = load_honesty_config(repo_root)
    private_key, pubkey = generate_ed25519_keypair()
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    body["ts"] = "2026-01-02T00:00:00Z"
    body = attach_signed_provenance(body, pubkey_token=pubkey)
    body = sign_append_body(
        body,
        kind="verdict",
        prev_hash=genesis["entry_hash"],
        private_key=private_key,
        pubkey_token=pubkey,
    )
    assert append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    ).exit_code == 0
    entries = read_ledger_entries(ledger)
    return entries[-1], private_key


def test_verify_idempotent_with_signatures(repo_root) -> None:
    _append_signed_verdict(repo_root)
    config = load_honesty_config(repo_root)
    first = verify_ledger_file(config=config, repo_root=repo_root)
    second = verify_ledger_file(config=config, repo_root=repo_root)
    assert first.exit_code == 0
    assert second.exit_code == 0


def test_body_tamper_flips_22(repo_root) -> None:
    entry, _ = _append_signed_verdict(repo_root)
    config = load_honesty_config(repo_root)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    tampered = dict(entry)
    tampered["passed"] = False
    ledger.write_text(
        serialize_entry(build_genesis_entry(ts="2026-01-01T00:00:00Z")) + serialize_entry(tampered),
        encoding="utf-8",
    )
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 22


def test_sig_tamper_flips_25(repo_root) -> None:
    entry, _ = _append_signed_verdict(repo_root)
    config = load_honesty_config(repo_root)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    tampered = dict(entry)
    tampered["provenance"] = dict(entry["provenance"])
    tampered["provenance"]["sig"] = "ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
    ledger.write_text(
        serialize_entry(build_genesis_entry(ts="2026-01-01T00:00:00Z")) + serialize_entry(tampered),
        encoding="utf-8",
    )
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 25


def test_excising_sig_does_not_change_entry_hash(repo_root) -> None:
    entry, _ = _append_signed_verdict(repo_root)
    with_sig_hash = compute_entry_hash(entry)
    stripped = dict(entry)
    stripped["provenance"] = {key: val for key, val in entry["provenance"].items() if key != "sig"}
    without_sig_hash = compute_entry_hash(stripped)
    assert with_sig_hash == without_sig_hash


def test_verify_chain_direct_mix(repo_root) -> None:
    entry, _ = _append_signed_verdict(repo_root)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    entries = read_ledger_entries(ledger)
    assert verify_chain(entries, regime="git-only") == 0
    assert entry["provenance"]["sig"].startswith("ed25519:")


def test_verify_flags_malformed_provenance_exit_2(repo_root) -> None:
    """§P0.6: `verify` must emit exit 2 on a hash-consistent but malformed provenance.

    A tamperer who inserts an unknown provenance key and recomputes ``entry_hash``
    keeps the chain hash-consistent (so it is not a ``22``); the structural defect
    must still surface as ``2`` — the malformed-provenance code the frozen contract
    names for ``verify``.
    """
    config = load_honesty_config(repo_root)
    genesis = build_genesis_entry(ts="2026-01-01T00:00:00Z")
    entry = {
        "v": 1,
        "ts": "2026-01-02T00:00:00Z",
        "kind": "hook_check",
        "actor_role": "overseer",
        "actor_session_id": "s1",
        "hook": "handoff",
        "ok": True,
        "prev_hash": genesis["entry_hash"],
        "provenance": {"agent_id": "a", "model_id": "m", "rogue": True},
    }
    entry["entry_hash"] = compute_entry_hash(entry)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(serialize_entry(genesis) + serialize_entry(entry), encoding="utf-8")
    entries = read_ledger_entries(ledger)
    assert verify_chain(entries, regime="git-only") == 2
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 2

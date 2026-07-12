"""Integration tests for Track P / P1 provenance (§P0.8)."""

from __future__ import annotations

import yaml

from adapters.config import load_config
from tests.support import (
    attach_signed_provenance,
    generate_ed25519_keypair,
    load_honesty_config,
    load_honesty_entry,
    sign_append_body,
)
from tools.honesty.genesis import build_genesis_entry
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.ledger_io import serialize_entry
from tools.honesty.types import LedgerAppendOptions


def _seed_genesis(repo_root, *, ts: str = "2026-01-01T00:00:00Z") -> dict:
    genesis = build_genesis_entry(ts=ts)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(serialize_entry(genesis), encoding="utf-8")
    return genesis


def test_append_with_soft_provenance(repo_root) -> None:
    config = load_honesty_config(repo_root)
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    body["provenance"] = {"agent_id": "cursor-agent", "model_id": "gpt-5.6"}
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    assert result.exit_code == 0
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 0


def test_append_with_signed_provenance(repo_root) -> None:
    config = load_honesty_config(repo_root)
    genesis = _seed_genesis(repo_root)
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
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    assert result.exit_code == 0
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 0


def test_verify_bad_signature_exit_25(repo_root) -> None:
    config = load_honesty_config(repo_root)
    genesis = _seed_genesis(repo_root)
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
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    lines = ledger.read_text(encoding="utf-8").strip().splitlines()
    entry = __import__("json").loads(lines[-1])
    entry["provenance"]["sig"] = "ed25519:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
    lines[-1] = __import__("json").dumps(entry, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 25


def test_require_agent_signature_gate_on_verdict(repo_root) -> None:
    load_honesty_config(repo_root)
    cfg = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["vcs"]["regime"] = "muse+git-mirror"
    data["vcs"]["canonical"] = "muse"
    data["vcs"]["muse"]["staging_remote"] = "staging"
    data["vcs"]["muse"]["main_branch"] = "main"
    data["vcs"]["git"]["mirror_branch"] = "muse-mirror"
    data["honesty"]["require_agent_signature"] = True
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg)
    body = load_honesty_entry(repo_root, "verdict-pass.json")
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    assert result.exit_code == 26

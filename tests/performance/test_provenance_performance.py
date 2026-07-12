"""Performance bounds for provenance signature verification (§P0.8)."""

from __future__ import annotations

import time

from tests.support import (
    attach_signed_provenance,
    generate_ed25519_keypair,
    load_honesty_config,
    sign_append_body,
)
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.genesis import build_genesis_entry
from tools.honesty.ledger import verify_ledger_file
from tools.honesty.ledger_io import serialize_entry


def test_signed_verify_2k_bounded(repo_root) -> None:
    config = load_honesty_config(repo_root)
    private_key, pubkey = generate_ed25519_keypair()
    genesis = build_genesis_entry(ts="2026-01-01T00:00:00Z")
    prev = genesis["entry_hash"]
    lines = [serialize_entry(genesis)]

    for index in range(2000):
        body = {
            "v": 1,
            "ts": f"2026-01-01T00:{index // 60:02d}:{index % 60:02d}Z",
            "kind": "hook_check",
            "actor_role": "overseer",
            "actor_session_id": f"p-{index}",
            "hook": "handoff",
            "ok": True,
        }
        body = attach_signed_provenance(
            body,
            pubkey_token=pubkey,
            agent_id=f"agent-{index}",
        )
        signed = sign_append_body(
            body,
            kind="hook_check",
            prev_hash=prev,
            private_key=private_key,
            pubkey_token=pubkey,
        )
        entry = dict(signed)
        entry["prev_hash"] = prev
        entry["entry_hash"] = compute_entry_hash(entry)
        prev = entry["entry_hash"]
        lines.append(serialize_entry(entry))

    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("".join(lines), encoding="utf-8")

    start = time.monotonic()
    result = verify_ledger_file(config=config, repo_root=repo_root)
    elapsed = time.monotonic() - start
    assert result.exit_code == 0
    assert elapsed < 8.0

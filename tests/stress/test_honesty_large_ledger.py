"""Stress tests for large honesty ledgers."""

from __future__ import annotations

from tests.support import honesty_artifact_hash, load_honesty_config
from tools.honesty.ledger import verify_ledger_file
from tools.honesty.ledger_io import serialize_entry
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.ledger import append_entry


def test_verify_10k_lines(repo_root) -> None:
    config = load_honesty_config(repo_root)
    artifact_hash = honesty_artifact_hash(repo_root)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)

    body = {
        "actor_role": "verifier",
        "actor_session_id": "stress-verifier",
        "artifact_sha256": artifact_hash,
        "passed": True,
        "evidence": {"reexecuted": ["verify-step:stress"]},
    }
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )

    from tools.honesty.canonical import compute_entry_hash
    import json

    text = ledger.read_text(encoding="utf-8")
    last = json.loads(text.strip().splitlines()[-1])
    expected_prev = last["entry_hash"]
    extra_lines: list[str] = []
    for index in range(9998):
        entry = {
            "v": 1,
            "ts": "2026-01-01T00:00:00Z",
            "kind": "hook_check",
            "actor_role": "overseer",
            "actor_session_id": f"s-{index}",
            "hook": "register",
            "ok": True,
            "prev_hash": expected_prev,
        }
        entry["entry_hash"] = compute_entry_hash(entry)
        expected_prev = entry["entry_hash"]
        extra_lines.append(serialize_entry(entry))

    with ledger.open("a", encoding="utf-8") as handle:
        handle.write("".join(extra_lines))

    result = verify_ledger_file(config=config, repo_root=repo_root)
    assert result.exit_code == 0
    assert len(ledger.read_text(encoding="utf-8").strip().splitlines()) == 10000

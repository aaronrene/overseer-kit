"""Performance bounds for honesty ledger verify."""

from __future__ import annotations

import json
import time

from tests.support import honesty_artifact_hash, load_honesty_config
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.ledger import verify_ledger_file
from tools.honesty.ledger_io import serialize_entry
from tools.honesty.ledger import append_entry
from tools.honesty.types import LedgerAppendOptions


def test_verify_10k_bounded(repo_root) -> None:
    config = load_honesty_config(repo_root)
    artifact_hash = honesty_artifact_hash(repo_root)
    body = {
        "actor_role": "verifier",
        "actor_session_id": "perf-verifier",
        "artifact_sha256": artifact_hash,
        "passed": True,
        "evidence": {"reexecuted": ["verify-step:perf"]},
    }
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    text = ledger.read_text(encoding="utf-8")
    last = json.loads(text.strip().splitlines()[-1])
    expected_prev = last["entry_hash"]
    extra: list[str] = []
    for index in range(9998):
        entry = {
            "v": 1,
            "ts": "2026-01-01T00:00:00Z",
            "kind": "hook_check",
            "actor_role": "overseer",
            "actor_session_id": f"p-{index}",
            "hook": "handoff",
            "ok": True,
            "prev_hash": expected_prev,
        }
        entry["entry_hash"] = compute_entry_hash(entry)
        expected_prev = entry["entry_hash"]
        extra.append(serialize_entry(entry))
    ledger.write_text(text + "".join(extra), encoding="utf-8")

    start = time.monotonic()
    result = verify_ledger_file(config=config, repo_root=repo_root)
    elapsed = time.monotonic() - start
    assert result.exit_code == 0
    assert elapsed < 5.0

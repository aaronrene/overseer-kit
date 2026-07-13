"""Performance bounds for P-evidence append/verify (§PE.10)."""

from __future__ import annotations

import time

from tests.fixtures.p_evidence import load_p_evidence_entry, seed_p_evidence_repo
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions

_APPEND_VERIFY_BUDGET_S = 2.0
_MATCH_SCAN_BUDGET_S = 1.0


def test_realistic_evidence_append_verify_within_bound(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body["artifacts"].append(
        {
            "type": "screenshot",
            "sha256": "d" * 64,
            "ref": "docs/archive/verify/p-evidence-status.png",
        }
    )
    started = time.perf_counter()
    assert (
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="verification_evidence", body=body),
        ).exit_code
        == 0
    )
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 0
    elapsed = time.perf_counter() - started
    assert elapsed < _APPEND_VERIFY_BUDGET_S


def test_match_scan_linear_no_filesystem_walk(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    for round_num in range(1, 101):
        body = load_p_evidence_entry("verification-evidence-pass.json")
        body["round"] = round_num
        body["actor_session_id"] = f"bv-{round_num}"
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="verification_evidence", body=body),
        )
    started = time.perf_counter()
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-evidence",
        ),
    )
    elapsed = time.perf_counter() - started
    assert result.exit_code == 0
    assert elapsed < _MATCH_SCAN_BUDGET_S

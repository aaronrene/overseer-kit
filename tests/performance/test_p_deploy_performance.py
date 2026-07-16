"""Performance bounds for P-deploy Mode C (§PD.9)."""

from __future__ import annotations

import time

from tests.fixtures.p_deploy import load_p_deploy_entry, seed_p_deploy_repo
from tools.honesty.ledger import append_entry
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions

_MATCH_SCAN_BUDGET_S = 1.0


def test_mode_c_match_over_realistic_ledger_within_bound(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    for round_num in range(1, 51):
        body = load_p_deploy_entry("verification-test-output-only.json")
        body["round"] = round_num
        body["actor_session_id"] = f"bv-{round_num}"
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="verification_evidence", body=body),
        )
    deploy = load_p_deploy_entry("verification-with-deploy-health.json")
    deploy["round"] = 51
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=deploy),
    )
    started = time.perf_counter()
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            deploy_health="Track P / P-deploy",
        ),
    )
    elapsed = time.perf_counter() - started
    assert result.exit_code == 0
    assert elapsed < _MATCH_SCAN_BUDGET_S

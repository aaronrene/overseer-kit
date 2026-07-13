"""Stress tests for P-deploy Mode C match scan (§PD.9)."""

from __future__ import annotations

import time

from tests.fixtures.p_deploy import load_p_deploy_entry, seed_p_deploy_repo
from tools.honesty.ledger import append_entry
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import find_matching_deploy_health

_MATCH_BUDGET_S = 2.0


def test_sparse_deploy_health_last_wins_over_many_entries(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    for round_num in range(1, 101):
        body = load_p_deploy_entry("verification-test-output-only.json")
        body["round"] = round_num
        body["actor_session_id"] = f"bv-{round_num}"
        assert (
            append_entry(
                config=config,
                repo_root=repo_root,
                options=LedgerAppendOptions(kind="verification_evidence", body=body),
            ).exit_code
            == 0
        )

    deploy_body = load_p_deploy_entry("verification-with-deploy-health.json")
    deploy_body["round"] = 101
    deploy_body["actor_session_id"] = "bv-deploy"
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=deploy_body),
    )

    more = load_p_deploy_entry("verification-test-output-only.json")
    more["round"] = 102
    more["actor_session_id"] = "bv-after"
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=more),
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
    assert elapsed < _MATCH_BUDGET_S

    from tools.honesty.ledger_io import read_ledger_entries
    from cli.paths import confine_path

    entries = read_ledger_entries(confine_path(repo_root, config.honesty.ledger))
    winner = find_matching_deploy_health(
        entries,
        phase_id="Track P / P-deploy",
        frozen_spec=None,
    )
    assert winner is not None
    assert winner["round"] == 101
    assert winner["actor_session_id"] == "bv-deploy"

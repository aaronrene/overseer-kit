"""Data-integrity tests for P-deploy Mode C matching (§PD.9)."""

from __future__ import annotations

import json

from tests.fixtures.p_deploy import load_p_deploy_entry, seed_p_deploy_repo
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import find_matching_deploy_health


def test_mode_c_match_depends_on_artifact_type_string(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    body = load_p_deploy_entry("verification-with-deploy-health.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    text = ledger.read_text(encoding="utf-8")
    # Tamper type after write — breaks hash chain (22) OR if we only read raw for match, fail match.
    lines = text.strip().splitlines()
    last = json.loads(lines[-1])
    last["artifacts"][1]["type"] = "screenshot"
    # Keep entry_hash stale so verify fails
    lines[-1] = json.dumps(last, separators=(",", ":"), sort_keys=True)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
    verify = verify_ledger_file(config=config, repo_root=repo_root)
    assert verify.exit_code == 22


def test_tampered_deploy_health_sha256_breaks_verify(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root)
    body = load_p_deploy_entry("verification-with-deploy-health.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    text = ledger.read_text(encoding="utf-8")
    ledger.write_text(text.replace("dddddddd", "eeeeeeee", 1), encoding="utf-8")
    verify = verify_ledger_file(config=config, repo_root=repo_root)
    assert verify.exit_code == 22


def test_append_embeds_hashes_refs_only_no_health_body(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root)
    health_path = repo_root / "artifacts" / "deploy-health.json"
    raw = health_path.read_text(encoding="utf-8")
    body = load_p_deploy_entry("verification-with-deploy-health.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    ledger_text = (repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl").read_text(
        encoding="utf-8"
    )
    assert '"status":"ok"' not in ledger_text
    assert raw.strip() not in ledger_text


def test_type_mismatch_fails_mode_c_match_without_tamper(repo_root) -> None:
    entry = load_p_deploy_entry("verification-with-deploy-health.json")
    entry["artifacts"][1]["type"] = "screenshot"
    assert (
        find_matching_deploy_health(
            [entry],
            phase_id="Track P / P-deploy",
            frozen_spec=None,
        )
        is None
    )


def test_validation_failure_no_partial_write(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    before = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    body = load_p_deploy_entry("verification-with-deploy-health.json")
    body["artifacts"] = []
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    assert result.exit_code == 24
    after = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    # genesis may auto-create; ensure no verification_evidence kind written
    assert "deploy_health" not in after or before == after
    if after != before:
        # only genesis allowed
        lines = [json.loads(line) for line in after.strip().splitlines()]
        assert all(line.get("kind") == "genesis" for line in lines)

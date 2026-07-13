"""Stress tests for P-evidence large artifact lists (§PE.10)."""

from __future__ import annotations

from tests.fixtures.p_evidence import load_p_evidence_entry, seed_p_evidence_repo
from tools.honesty.canonical import canonical_json, compute_entry_hash
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.types import LedgerAppendOptions


def test_large_artifacts_append_and_verify(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body["artifacts"] = [
        {
            "type": "test_output",
            "sha256": f"{index:064x}",
            "ref": f"capture-{index}",
        }
        for index in range(50)
    ]
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    assert result.exit_code == 0
    verify = verify_ledger_file(config=config, repo_root=repo_root)
    assert verify.exit_code == 0


def test_many_evidence_entries_chain_verify(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    for round_num in range(1, 21):
        body = load_p_evidence_entry("verification-evidence-pass.json")
        body["round"] = round_num
        body["actor_session_id"] = f"bv-{round_num}"
        code = append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="verification_evidence", body=body),
        ).exit_code
        assert code == 0
    verify = verify_ledger_file(config=config, repo_root=repo_root)
    assert verify.exit_code == 0


def test_artifact_order_affects_canonical_hash() -> None:
    first = [{"type": "test_output", "sha256": "a" * 64}, {"type": "screenshot", "sha256": "b" * 64, "ref": "x.png"}]
    second = list(reversed(first))
    h1 = compute_entry_hash({"artifacts": first, "kind": "verification_evidence", "v": 1})
    h2 = compute_entry_hash({"artifacts": second, "kind": "verification_evidence", "v": 1})
    assert h1 != h2
    assert canonical_json({"artifacts": first}) != canonical_json({"artifacts": second})

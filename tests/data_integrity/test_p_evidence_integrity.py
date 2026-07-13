"""Data-integrity tests for P-evidence ledger hashing (§PE.10)."""

from __future__ import annotations

import json

import pytest

from tests.fixtures.p_evidence import load_p_evidence_entry, seed_p_evidence_repo
from tools.honesty.ledger import append_entry, parse_append_body, verify_ledger_file
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import EntryValidationError, validate_append_body


def test_tampered_artifact_sha256_breaks_verify(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    body = load_p_evidence_entry("verification-evidence-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    text = ledger.read_text(encoding="utf-8")
    ledger.write_text(text.replace("bbbbbbbb", "cccccccc", 1), encoding="utf-8")
    verify = verify_ledger_file(config=config, repo_root=repo_root)
    assert verify.exit_code == 22


def test_append_does_not_embed_file_bytes(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    image = repo_root / "docs" / "archive" / "verify" / "p-evidence-status.png"
    raw = image.read_bytes()
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body["artifacts"].append(
        {
            "type": "screenshot",
            "sha256": "c" * 64,
            "ref": "docs/archive/verify/p-evidence-status.png",
        }
    )
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    ledger_text = (repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl").read_text(encoding="utf-8")
    assert raw.hex() not in ledger_text
    assert "PNG" not in ledger_text


def test_path_escape_append_file_refused(repo_root) -> None:
    outside = repo_root.parent / "escaped.json"
    outside.write_text(json.dumps(load_p_evidence_entry("verification-evidence-pass.json")), encoding="utf-8")
    body, code, _ = parse_append_body(
        repo_root=repo_root,
        file_path=str(outside),
        stdin_text=None,
    )
    assert code == 4


def test_validation_failure_no_partial_write(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    before = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body["artifacts"] = []
    with pytest.raises(EntryValidationError):
        validate_append_body(kind="verification_evidence", body=body)
    after = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    assert after == before


def test_idempotent_verify(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    body = load_p_evidence_entry("verification-evidence-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    first = verify_ledger_file(config=config, repo_root=repo_root)
    second = verify_ledger_file(config=config, repo_root=repo_root)
    assert first.exit_code == second.exit_code == 0

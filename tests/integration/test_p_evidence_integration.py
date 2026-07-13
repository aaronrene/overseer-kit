"""Integration tests for P-evidence ledger append and Mode B honesty-status (§PE.10)."""

from __future__ import annotations

import json

import yaml

from tests.fixtures.p_evidence import load_p_evidence_entry, seed_p_evidence_repo
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions


def _append_evidence(repo_root, body_name: str = "verification-evidence-pass.json") -> int:
    config = seed_p_evidence_repo(repo_root)
    body = load_p_evidence_entry(body_name)
    return append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    ).exit_code


def test_append_verification_evidence_writes_chain(repo_root) -> None:
    assert _append_evidence(repo_root) == 0
    config = seed_p_evidence_repo(repo_root)
    verify = verify_ledger_file(config=config, repo_root=repo_root)
    assert verify.exit_code == 0


def test_mode_b_require_missing_exit_33(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root, require_verification_evidence="require")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-evidence",
        ),
    )
    assert result.exit_code == 33
    assert result.json_payload.error == "missing_verification_evidence"
    assert result.json_payload.verification_evidence is not None


def test_mode_b_matching_pass_exit_0(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root, require_verification_evidence="require")
    body = load_p_evidence_entry("verification-evidence-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-evidence",
            frozen_spec="docs/PHASE-TRACK-P-P-EVIDENCE.md",
        ),
    )
    assert result.exit_code == 0
    assert result.json_payload.verification_evidence["matched_entry_hash"] is not None


def test_mode_b_warn_missing_exit_0_with_warning(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root, require_verification_evidence="warn")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-evidence",
        ),
    )
    assert result.exit_code == 0
    assert "warning:" in result.stderr_extra


def test_mode_b_off_not_enforced(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root, require_verification_evidence="off")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-evidence",
        ),
    )
    assert result.exit_code == 0
    assert result.json_payload.verification_evidence["matched_entry_hash"] is None


def test_mode_a_and_b_combined_exit_1(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook="board_done",
            artifact="artifacts/sample.txt",
            verification_evidence="Track P / P-evidence",
        ),
    )
    assert result.exit_code == 1


def test_mode_a_unchanged_without_mode_b(repo_root) -> None:
    from tests.support import load_honesty_config

    config = load_honesty_config(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 20
    assert result.json_payload.verification_evidence is None


def test_honesty_disabled_mode_b_exit_4(repo_root) -> None:
    seed_p_evidence_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["enabled"] = False
    data["modules"]["honesty"]["enabled"] = False
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    from adapters.config import load_config

    config = load_config(cfg_path)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-evidence",
        ),
    )
    assert result.exit_code == 4

"""Integration tests for P-deploy Mode C honesty-status (§PD.9)."""

from __future__ import annotations

import yaml

from tests.fixtures.p_deploy import load_p_deploy_entry, seed_p_deploy_repo
from tools.honesty.ledger import append_entry
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions


def test_mode_c_require_missing_exit_34(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 34
    assert result.json_payload.error == "missing_deploy_health"
    assert result.json_payload.deploy_health is not None
    assert result.json_payload.verification_evidence is None


def test_mode_c_matching_deploy_health_exit_0(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    body = load_p_deploy_entry("verification-with-deploy-health.json")
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
            deploy_health="Track P / P-deploy",
            frozen_spec="docs/archive/phases/PHASE-TRACK-P-P-DEPLOY.md",
        ),
    )
    assert result.exit_code == 0
    assert result.json_payload.deploy_health["matched_entry_hash"] is not None
    assert result.json_payload.verification_evidence is None


def test_mode_c_test_output_only_does_not_satisfy(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    body = load_p_deploy_entry("verification-test-output-only.json")
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
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 34
    assert result.json_payload.error == "missing_deploy_health"


def test_mode_c_warn_missing_exit_0_with_warning(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="warn")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 0
    assert "warning:" in result.stderr_extra
    assert "deploy_health" in result.stderr_extra


def test_mode_c_off_not_enforced(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="off")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 0
    assert result.json_payload.ok is True
    assert result.json_payload.deploy_health["matched_entry_hash"] is None
    assert result.json_payload.error is None


def test_mode_a_b_c_combined_exit_1(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook="board_done",
            artifact="artifacts/sample.txt",
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 1

    result_bc = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-deploy",
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result_bc.exit_code == 1


def test_mode_a_and_b_unchanged_without_mode_c(repo_root) -> None:
    from tests.support import load_honesty_config

    config = load_honesty_config(repo_root)
    mode_a = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert mode_a.exit_code == 20
    assert mode_a.json_payload.deploy_health is None
    assert mode_a.json_payload.verification_evidence is None

    config_b = seed_p_deploy_repo(repo_root, require_verification_evidence="require")
    mode_b = run_honesty_status(
        config=config_b,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            verification_evidence="Track P / P-deploy",
        ),
    )
    assert mode_b.exit_code == 33
    assert mode_b.json_payload.deploy_health is None
    assert mode_b.json_payload.verification_evidence is not None


def test_honesty_disabled_mode_c_exit_4(repo_root) -> None:
    seed_p_deploy_repo(repo_root, require_deploy_health="require")
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
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 4

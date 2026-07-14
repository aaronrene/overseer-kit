"""End-to-end P-deploy Mode C CLI tests (§PD.9)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.fixtures.p_deploy import (
    FIXTURES,
    copy_p_deploy_entries,
    load_p_deploy_entry,
    seed_p_deploy_repo,
)
from tests.support import git_status_runner, muse_mirror_status_runner, run_cli, seed_muse_substrate


def _append_evidence(tmp_path: Path, body_name: str) -> int:
    copy_p_deploy_entries(tmp_path)
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(load_p_deploy_entry(body_name)), encoding="utf-8")
    return run_cli(
        ["ledger", "append", "--kind", "verification_evidence", "--file", "payload.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )


def test_e2e_mode_b_may_match_mode_c_misses_then_deploy_health_last_wins(
    tmp_path: Path, capsys
) -> None:
    seed_p_deploy_repo(
        tmp_path,
        require_deploy_health="require",
        require_verification_evidence="require",
    )
    assert _append_evidence(tmp_path, "verification-test-output-only.json") == 0

    code_b = run_cli(
        [
            "honesty-status",
            "--verification-evidence",
            "Track P / P-deploy",
            "--json",
        ],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code_b == 0
    payload_b = json.loads(capsys.readouterr().out)
    assert payload_b["verification_evidence"]["matched_entry_hash"] is not None
    assert "deploy_health" not in payload_b

    code_c_miss = run_cli(
        ["honesty-status", "--deploy-health", "Track P / P-deploy", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code_c_miss == 34
    payload_miss = json.loads(capsys.readouterr().out)
    assert payload_miss["error"] == "missing_deploy_health"
    assert "verification_evidence" not in payload_miss

    body = load_p_deploy_entry("verification-with-deploy-health.json")
    second = tmp_path / "second.json"
    second.write_text(json.dumps(body), encoding="utf-8")
    assert run_cli(
        ["ledger", "append", "--kind", "verification_evidence", "--file", "second.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    ) == 0

    code_c = run_cli(
        [
            "honesty-status",
            "--deploy-health",
            "Track P / P-deploy",
            "--frozen-spec",
            "docs/PHASE-TRACK-P-P-DEPLOY.md",
            "--json",
        ],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code_c == 0
    payload_c = json.loads(capsys.readouterr().out)
    ledger = (tmp_path / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl").read_text(encoding="utf-8")
    last_line = json.loads(ledger.strip().splitlines()[-1])
    assert payload_c["deploy_health"]["matched_entry_hash"] == last_line["entry_hash"]


def test_skill_normative_deploy_pass_includes_deploy_health() -> None:
    fixture = json.loads((FIXTURES / "skill-pass-body.json").read_text(encoding="utf-8"))
    body = load_p_deploy_entry("verification-with-deploy-health.json")
    assert body["bv_verdict"] == fixture["bv_verdict"]
    types = {item["type"] for item in body["artifacts"]}
    for required in fixture["required_artifact_types_for_deploy_pass"]:
        assert required in types


def test_e2e_git_only_and_muse_regime_unsigned_mode_c(tmp_path: Path) -> None:
    for regime in ("config-git-only.yaml", "config-muse-git-mirror.yaml"):
        repo = tmp_path / regime
        repo.mkdir()
        seed_p_deploy_repo(repo, require_deploy_health="require", regime_config=regime)
        if "muse" in regime:
            seed_muse_substrate(repo)
        copy_p_deploy_entries(repo)
        payload = repo / "payload.json"
        payload.write_text(
            json.dumps(load_p_deploy_entry("verification-with-deploy-health.json")),
            encoding="utf-8",
        )
        runner = muse_mirror_status_runner(repo) if "muse" in regime else git_status_runner()
        assert run_cli(
            ["ledger", "append", "--kind", "verification_evidence", "--file", "payload.json"],
            cwd=repo,
            runner=runner,
            kit=kit_root(),
        ) == 0
        assert run_cli(
            ["honesty-status", "--deploy-health", "Track P / P-deploy", "--json"],
            cwd=repo,
            runner=runner,
            kit=kit_root(),
            json_mode=True,
        ) == 0

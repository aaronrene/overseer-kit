"""End-to-end P-evidence CLI tests (§PE.10)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from cli.kit_root import kit_root
from tests.fixtures.p_evidence import (
    FIXTURES,
    copy_p_evidence_entries,
    load_p_evidence_entry,
    seed_p_evidence_repo,
)
from tests.support import git_status_runner, muse_mirror_status_runner, run_cli, seed_muse_substrate


def _append_evidence(tmp_path: Path, body_name: str) -> int:
    copy_p_evidence_entries(tmp_path)
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(load_p_evidence_entry(body_name)), encoding="utf-8")
    return run_cli(
        ["ledger", "append", "--kind", "verification_evidence", "--file", "payload.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )


def test_e2e_append_show_and_mode_b_match(tmp_path: Path, capsys) -> None:
    seed_p_evidence_repo(tmp_path, require_verification_evidence="require")
    assert _append_evidence(tmp_path, "verification-evidence-pass.json") == 0
    show_code = run_cli(
        ["ledger", "show", "--last", "3"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert show_code == 0
    out = capsys.readouterr().out
    assert "verification_evidence" in out

    code = run_cli(
        [
            "honesty-status",
            "--verification-evidence",
            "Track P / P-evidence",
            "--frozen-spec",
            "docs/PHASE-TRACK-P-P-EVIDENCE.md",
            "--json",
        ],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verification_evidence"]["matched_entry_hash"] is not None


def test_e2e_last_wins_findings_then_pass(tmp_path: Path, capsys) -> None:
    seed_p_evidence_repo(tmp_path, require_verification_evidence="require")
    assert _append_evidence(tmp_path, "verification-evidence-findings.json") == 0
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body["round"] = 2
    second = tmp_path / "second.json"
    second.write_text(json.dumps(body), encoding="utf-8")
    assert run_cli(
        ["ledger", "append", "--kind", "verification_evidence", "--file", "second.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    ) == 0
    code = run_cli(
        [
            "honesty-status",
            "--verification-evidence",
            "Track P / P-evidence",
            "--json",
        ],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    ledger = (tmp_path / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl").read_text(encoding="utf-8")
    last_line = json.loads(ledger.strip().splitlines()[-1])
    assert last_line["bv_verdict"] == "pass"
    assert payload["verification_evidence"]["matched_entry_hash"] == last_line["entry_hash"]


def test_skill_normative_pass_body_includes_test_output() -> None:
    fixture = json.loads((FIXTURES / "skill-pass-body.json").read_text(encoding="utf-8"))
    body = load_p_evidence_entry("verification-evidence-pass.json")
    assert body["bv_verdict"] == fixture["bv_verdict"]
    types = {item["type"] for item in body["artifacts"]}
    assert "test_output" in types
    for required in fixture["required_artifact_types_for_pass"]:
        assert required in types


def test_e2e_git_only_and_muse_regime_unsigned(tmp_path: Path) -> None:
    for regime in ("config-git-only.yaml", "config-muse-git-mirror.yaml"):
        repo = tmp_path / regime
        repo.mkdir()
        seed_p_evidence_repo(repo, require_verification_evidence="require", regime_config=regime)
        if "muse" in regime:
            seed_muse_substrate(repo)
        copy_p_evidence_entries(repo)
        payload = repo / "payload.json"
        payload.write_text(json.dumps(load_p_evidence_entry("verification-evidence-pass.json")), encoding="utf-8")
        runner = muse_mirror_status_runner(repo) if "muse" in regime else git_status_runner()
        assert run_cli(
            ["ledger", "append", "--kind", "verification_evidence", "--file", "payload.json"],
            cwd=repo,
            runner=runner,
            kit=kit_root(),
        ) == 0
        assert run_cli(
            ["honesty-status", "--verification-evidence", "Track P / P-evidence", "--json"],
            cwd=repo,
            runner=runner,
            kit=kit_root(),
            json_mode=True,
        ) == 0

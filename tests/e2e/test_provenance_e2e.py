"""End-to-end CLI tests for Track P / P1 provenance (§P0.8)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from cli.kit_root import kit_root
from tests.support import (
    attach_signed_provenance,
    generate_ed25519_keypair,
    git_status_runner,
    honesty_artifact_hash,
    load_honesty_entry,
    run_cli,
    seed_honesty_repo,
    sign_append_body,
)
from tools.honesty.genesis import build_genesis_entry
from tools.honesty.ledger_io import serialize_entry


def _enable_muse_signature_requirement(tmp_path: Path) -> None:
    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["vcs"]["regime"] = "muse+git-mirror"
    data["vcs"]["canonical"] = "muse"
    data["vcs"]["muse"]["staging_remote"] = "staging"
    data["vcs"]["muse"]["main_branch"] = "main"
    data["vcs"]["git"]["mirror_branch"] = "muse-mirror"
    data["honesty"]["require_agent_signature"] = True
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_e2e_signed_verdict_and_verify_green(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    genesis = build_genesis_entry(ts="2026-01-01T00:00:00Z")
    ledger = tmp_path / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(serialize_entry(genesis), encoding="utf-8")
    private_key, pubkey = generate_ed25519_keypair()
    artifact_hash = honesty_artifact_hash(tmp_path)
    body = load_honesty_entry(tmp_path, "verdict-pass.json", artifact_hash=artifact_hash)
    body["ts"] = "2026-01-02T00:00:00Z"
    body = attach_signed_provenance(body, pubkey_token=pubkey)
    body = sign_append_body(
        body,
        kind="verdict",
        prev_hash=genesis["entry_hash"],
        private_key=private_key,
        pubkey_token=pubkey,
    )
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(body), encoding="utf-8")
    assert (
        run_cli(
            ["ledger", "append", "--kind", "verdict", "--file", "payload.json"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 0
    )
    assert run_cli(["ledger", "verify"], cwd=tmp_path, runner=git_status_runner(), kit=kit_root()) == 0


def test_e2e_git_only_unsigned_cycle_still_green(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    artifact_hash = honesty_artifact_hash(tmp_path)
    body = load_honesty_entry(tmp_path, "verdict-pass.json", artifact_hash=artifact_hash)
    body["provenance"] = {"agent_id": "cursor-agent", "model_id": "gpt-5.6"}
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(body), encoding="utf-8")
    assert (
        run_cli(
            ["ledger", "append", "--kind", "verdict", "--file", "payload.json"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 0
    )
    assert (
        run_cli(
            ["honesty-status", "--hook", "handoff", "--artifact", "artifacts/sample.txt", "--json"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            json_mode=True,
        )
        == 0
    )


def test_e2e_git_only_require_agent_signature_config_exit_26(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["honesty"]["require_agent_signature"] = True
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    code = run_cli(["ledger", "verify"], cwd=tmp_path, runner=git_status_runner(), kit=kit_root())
    assert code == 26


def test_e2e_muse_required_signature_unsigned_verdict_exit_26(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    _enable_muse_signature_requirement(tmp_path)
    artifact_hash = honesty_artifact_hash(tmp_path)
    body = load_honesty_entry(tmp_path, "verdict-pass.json", artifact_hash=artifact_hash)
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(body), encoding="utf-8")
    code = run_cli(
        ["ledger", "append", "--kind", "verdict", "--file", "payload.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 26

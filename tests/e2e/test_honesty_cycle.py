"""End-to-end honesty CLI tests."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from cli.kit_root import kit_root
from tests.support import git_status_runner, honesty_artifact_hash, load_honesty_entry, run_cli, seed_honesty_repo


def _append_verdict(tmp_path: Path, body_name: str = "verdict-pass.json") -> int:
    artifact_hash = honesty_artifact_hash(tmp_path)
    entry_path = tmp_path / "entries" / body_name
    text = entry_path.read_text(encoding="utf-8").replace("PLACEHOLDER", artifact_hash)
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(text, encoding="utf-8")
    return run_cli(
        ["ledger", "append", "--kind", "verdict", "--file", "payload.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )


def test_cli_producer_cannot_append_verdict(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    code = _append_verdict(tmp_path, "verdict-producer.json")
    assert code == 23


def test_cli_missing_verdict_exit_20(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    code = run_cli(
        ["honesty-status", "--hook", "board_done", "--artifact", "artifacts/sample.txt", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 20


def test_cli_tampered_line_exit_22(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    assert _append_verdict(tmp_path) == 0
    ledger = tmp_path / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    text = ledger.read_text(encoding="utf-8")
    ledger.write_text(text.replace("verdict", "verdictx", 1), encoding="utf-8")
    code = run_cli(
        ["ledger", "verify"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 22


def test_cli_empty_evidence_exit_24(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    code = _append_verdict(tmp_path, "verdict-empty-evidence.json")
    assert code == 24


def test_cli_producer_session_rejects_same_session(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    assert _append_verdict(tmp_path, "verdict-same-session.json") == 0
    code = run_cli(
        [
            "honesty-status",
            "--hook",
            "board_done",
            "--artifact",
            "artifacts/sample.txt",
            "--producer-session",
            "producer-session-1",
            "--json",
        ],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 20


def test_cli_last_verdict_wins(tmp_path: Path, capsys) -> None:
    seed_honesty_repo(tmp_path)
    assert _append_verdict(tmp_path) == 0
    body = load_honesty_entry(tmp_path, "verdict-pass.json")
    body["actor_session_id"] = "verifier-session-2"
    second = tmp_path / "second.json"
    second.write_text(json.dumps(body), encoding="utf-8")
    assert run_cli(
        ["ledger", "append", "--kind", "verdict", "--file", "second.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    ) == 0
    code = run_cli(
        ["honesty-status", "--hook", "board_done", "--artifact", "artifacts/sample.txt", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    ledger = (tmp_path / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl").read_text(encoding="utf-8")
    last_line = json.loads(ledger.strip().splitlines()[-1])
    assert payload["matched_verdict_hash"] == last_line["entry_hash"]


def test_cli_unknown_hook_exit_1(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    code = run_cli(
        ["honesty-status", "--hook", "nope", "--artifact", "artifacts/sample.txt"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 1


def test_cli_subset_require_verdict_on_refuses(tmp_path: Path) -> None:
    seed_honesty_repo(tmp_path)
    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["honesty"]["require_verdict_on"] = ["handoff"]
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    code = run_cli(
        ["honesty-status", "--hook", "board_done", "--artifact", "artifacts/sample.txt"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 4

"""Unit tests for K10 honesty config, ledger, and status helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from adapters.errors import ConfigError
from tests.support import HONESTY, honesty_artifact_hash, load_honesty_config, seed_honesty_repo
from tools.honesty.canonical import canonical_json, compute_entry_hash
from tools.honesty.genesis import GENESIS_PREV, build_genesis_entry
from tools.honesty.ledger import append_entry, verify_chain
from tools.honesty.ledger_io import parse_jsonl_text, split_jsonl_lines
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import EntryValidationError, validate_append_body


def test_genesis_prev_constant() -> None:
    assert GENESIS_PREV == "368646f427571067ec853ef0c3d4cce9ecfa3fb3e003dd1252cd5d02f111e513"


def test_canonical_json_sorted_keys() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_entry_hash_omits_entry_hash_key() -> None:
    body = {"v": 1, "kind": "genesis", "ts": "2026-01-01T00:00:00Z", "prev_hash": GENESIS_PREV}
    h1 = compute_entry_hash(body)
    body["entry_hash"] = "deadbeef"
    h2 = compute_entry_hash(body)
    assert h1 == h2


def test_genesis_with_actors_refused() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(
            kind="genesis",
            body={"actor_role": "owner", "actor_session_id": "x"},
        )
    assert exc.value.exit_code == 2


def test_kind_body_mismatch_refused() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verdict", body={"kind": "genesis"})
    assert exc.value.exit_code == 2


def test_approval_recorded_requires_owner() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(
            kind="approval_recorded",
            body={
                "actor_role": "verifier",
                "actor_session_id": "s",
                "artifact_sha256": "aa",
                "bound_verdict_hash": "bb",
            },
        )
    assert exc.value.exit_code == 23


def test_verdict_empty_evidence_refused() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(
            kind="verdict",
            body={
                "actor_role": "verifier",
                "actor_session_id": "s",
                "artifact_sha256": "aa",
                "passed": True,
                "evidence": {"reexecuted": []},
            },
        )
    assert exc.value.exit_code == 24


def test_jsonl_trailing_empty_segment_ignored() -> None:
    text = '{"a":1}\n{"b":2}\n'
    assert split_jsonl_lines(text) == ['{"a":1}', '{"b":2}']
    assert len(parse_jsonl_text(text)) == 2


def test_honesty_disabled_refuses_before_paths(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["enabled"] = False
    data["modules"]["honesty"]["enabled"] = False
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg_path)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 4

    append = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body={}),
    )
    assert append.exit_code == 4


def test_require_verdict_on_empty_raises(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["require_verdict_on"] = []
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="must not be empty"):
        load_config(cfg_path)


def test_require_verdict_on_unknown_raises(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["require_verdict_on"] = ["nope"]
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="board_done"):
        load_config(cfg_path)


def test_hook_not_in_allowlist_refuses(repo_root: Path) -> None:
    config = load_honesty_config(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["require_verdict_on"] = ["handoff"]
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg_path)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 4


def test_roles_file_missing_refuses(repo_root: Path) -> None:
    config = load_honesty_config(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["roles_file"] = "missing-roles.yaml"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg_path)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 4


def test_roles_file_readable_warns_enum_only(repo_root: Path) -> None:
    config = load_honesty_config(repo_root)
    roles = repo_root / "roles.yaml"
    roles.write_text("custom: true\n", encoding="utf-8")
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["roles_file"] = "roles.yaml"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg_path)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 20
    assert "roles_file" in result.stderr_extra


def test_require_l1_evidence_prefix(repo_root: Path) -> None:
    config = load_honesty_config(repo_root)
    artifact_hash = honesty_artifact_hash(repo_root)
    body = json.loads((HONESTY / "entries" / "verdict-pass.json").read_text(encoding="utf-8"))
    body["artifact_sha256"] = artifact_hash
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result.exit_code == 0

    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["require_l1_evidence"] = "require"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg_path)
    body2 = body.copy()
    body2["actor_session_id"] = "verifier-2"
    body2["evidence"] = {"reexecuted": ["manual-check"], "notes": "no l1"}
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body2),
    )
    result2 = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(hook="board_done", artifact="artifacts/sample.txt"),
    )
    assert result2.exit_code == 20


def test_verify_chain_detects_break() -> None:
    genesis = build_genesis_entry("2026-01-01T00:00:00Z")
    bad = dict(genesis)
    bad["entry_hash"] = "0" * 64
    assert verify_chain([genesis]) == 0
    assert verify_chain([bad]) == 22

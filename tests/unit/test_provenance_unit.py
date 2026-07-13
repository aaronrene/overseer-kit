"""Unit tests for Track P / P1 provenance envelope (§P0.8)."""

from __future__ import annotations

import pytest

from adapters.config import load_config
from adapters.errors import ConfigError
from tests.support import (
    FIXTURES,
    generate_ed25519_keypair,
    seed_honesty_repo,
    sign_entry_hash,
    write_config,
)
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.ed25519_util import verify_ed25519_signature
from tools.honesty.genesis import GENESIS_PREV
from tools.honesty.provenance import validate_provenance
from tools.honesty.validate import EntryValidationError, validate_append_body


def test_provenance_required_fields() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_provenance({"agent_id": "a"})
    assert exc.value.exit_code == 2


def test_provenance_strict_keys() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_provenance({"agent_id": "a", "model_id": "m", "extra": True})
    assert exc.value.exit_code == 2


def test_provenance_sig_pubkey_pairing() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_provenance({"agent_id": "a", "model_id": "m", "sig": "ed25519:AA=="})
    assert exc.value.exit_code == 2


def test_compute_entry_hash_excludes_provenance_sig() -> None:
    private_key, pubkey = generate_ed25519_keypair()
    body = {
        "v": 1,
        "kind": "verdict",
        "ts": "2026-01-01T00:00:00Z",
        "prev_hash": GENESIS_PREV,
        "provenance": {
            "agent_id": "cursor-agent",
            "model_id": "gpt-5.6",
            "pubkey": pubkey,
        },
    }
    unsigned_hash = compute_entry_hash(body)
    body["provenance"]["sig"] = sign_entry_hash(private_key, unsigned_hash)
    assert compute_entry_hash(body) == unsigned_hash


def test_legacy_unsigned_entry_hash_unchanged() -> None:
    body = {
        "v": 1,
        "kind": "hook_check",
        "ts": "2026-01-01T00:00:00Z",
        "prev_hash": GENESIS_PREV,
        "actor_role": "overseer",
        "actor_session_id": "legacy",
        "hook": "handoff",
        "ok": True,
    }
    expected = "0044b277fdbebdf824a0dd6005dc5630a9fe4d65f5b01d029cdd7028f6122d4e"
    # Pin the legacy hash so regressions are caught if canonical rules drift.
    assert compute_entry_hash(body) == expected


def test_ed25519_sign_verify_round_trip() -> None:
    private_key, pubkey = generate_ed25519_keypair()
    entry_hash = "abc123" * 10 + "abcd"
    sig = sign_entry_hash(private_key, entry_hash)
    assert verify_ed25519_signature(pubkey_token=pubkey, entry_hash_hex=entry_hash, sig_token=sig)


def test_genesis_rejects_provenance() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(
            kind="genesis",
            body={"provenance": {"agent_id": "a", "model_id": "m"}},
        )
    assert exc.value.exit_code == 2


def test_soft_provenance_allowed_on_verdict() -> None:
    merged = validate_append_body(
        kind="verdict",
        body={
            "actor_role": "verifier",
            "actor_session_id": "v1",
            "artifact_sha256": "aa" * 32,
            "passed": True,
            "evidence": {"reexecuted": ["verify-step:x"]},
            "provenance": {"agent_id": "cursor-agent", "model_id": "gpt-5.6"},
        },
    )
    assert merged["provenance"]["agent_id"] == "cursor-agent"


def test_git_only_require_agent_signature_config_error_26(repo_root) -> None:
    seed_honesty_repo(repo_root)
    cfg = repo_root / ".overseer" / "config.yaml"
    import yaml

    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["honesty"]["require_agent_signature"] = True
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError) as exc:
        load_config(cfg)
    assert exc.value.exit_code == 26


def test_muse_regime_allows_require_agent_signature(tmp_path) -> None:
    write_config(tmp_path, "config-muse-git-mirror.yaml")
    cfg = tmp_path / ".overseer" / "config.yaml"
    import yaml

    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data.setdefault("honesty", {})["enabled"] = True
    data["honesty"]["ledger"] = ".overseer/honesty/VERDICT-LEDGER.jsonl"
    data["honesty"]["require_agent_signature"] = True
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg)
    assert config.honesty.require_agent_signature is True

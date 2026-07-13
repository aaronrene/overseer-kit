"""Security tests for Track P / P1 provenance (§P0.8)."""

from __future__ import annotations

import inspect
import json

import pytest
import yaml

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.kit_root import kit_root
from tests.support import git_status_runner, load_honesty_config, run_cli, seed_honesty_repo
from tools.honesty import ed25519_util, ledger, provenance, status


def test_kit_modules_do_not_load_private_keys() -> None:
    """Production honesty modules must not reference private-key APIs."""
    sources = (
        inspect.getsource(ed25519_util),
        inspect.getsource(provenance),
        inspect.getsource(ledger),
        inspect.getsource(status),
    )
    joined = "\n".join(sources)
    assert "PrivateKey" not in joined
    assert "private_key" not in joined


def test_malformed_sig_rejected_not_executed(repo_root) -> None:
    config = load_honesty_config(repo_root)
    body = {
        "actor_role": "verifier",
        "actor_session_id": "v1",
        "artifact_sha256": "aa" * 32,
        "passed": True,
        "evidence": {"reexecuted": ["verify-step:x"]},
        "provenance": {
            "agent_id": "cursor-agent",
            "model_id": "gpt-5.6",
            "pubkey": "ed25519:AA==",
            "sig": "__import__('os').system('echo pwned')",
        },
    }
    from tools.honesty.ledger import append_entry
    from tools.honesty.types import LedgerAppendOptions

    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verdict", body=body),
    )
    assert result.exit_code == 2


def test_provenance_strings_treated_as_opaque_data(tmp_path) -> None:
    seed_honesty_repo(tmp_path)
    payload = {
        "actor_role": "verifier",
        "actor_session_id": "v1",
        "artifact_sha256": "aa" * 32,
        "passed": True,
        "evidence": {"reexecuted": ["verify-step:x"]},
        "provenance": {
            "agent_id": "<script>alert(1)</script>",
            "model_id": "'; DROP TABLE ledger; --",
            "human_ref": "../../../etc/passwd",
        },
    }
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    code = run_cli(
        ["ledger", "append", "--kind", "verdict", "--file", "payload.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 0


def test_git_only_cannot_force_require_agent_signature(tmp_path) -> None:
    seed_honesty_repo(tmp_path)
    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["honesty"]["require_agent_signature"] = True
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError) as exc:
        load_config(cfg)
    assert exc.value.exit_code == 26

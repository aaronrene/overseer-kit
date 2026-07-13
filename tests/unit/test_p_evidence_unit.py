"""Unit tests for P-evidence verification_evidence schema (§PE.10)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from adapters.config import HONESTY_KEYS, load_config
from tests.fixtures.p_evidence import load_p_evidence_entry
from tests.support import seed_honesty_repo
from tools.honesty.types import BV_VERDICTS, ENTRY_KINDS, VERIFICATION_ARTIFACT_TYPES
from tools.honesty.validate import EntryValidationError, validate_append_body, validate_verification_artifacts


def _minimal_body(**overrides) -> dict:
    body = load_p_evidence_entry("verification-evidence-pass.json")
    body.update(overrides)
    return body


def test_verification_evidence_in_entry_kinds() -> None:
    assert "verification_evidence" in ENTRY_KINDS
    assert VERIFICATION_ARTIFACT_TYPES == frozenset({"test_output", "deploy_health", "screenshot"})
    assert BV_VERDICTS == frozenset({"pass", "findings", "blocked"})


def test_validate_accepts_minimal_verification_evidence() -> None:
    validated = validate_append_body(kind="verification_evidence", body=_minimal_body())
    assert validated["kind"] == "verification_evidence"
    assert validated["artifacts"][0]["type"] == "test_output"


def test_unknown_artifact_type_exit_2() -> None:
    body = _minimal_body(artifacts=[{"type": "video", "sha256": "a" * 64}])
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verification_evidence", body=body)
    assert exc.value.exit_code == 2


def test_uppercase_sha256_exit_2() -> None:
    body = _minimal_body(
        artifacts=[{"type": "test_output", "sha256": "B" * 64}],
    )
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verification_evidence", body=body)
    assert exc.value.exit_code == 2


def test_short_sha256_exit_2() -> None:
    body = _minimal_body(artifacts=[{"type": "test_output", "sha256": "abc"}])
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verification_evidence", body=body)
    assert exc.value.exit_code == 2


def test_deploy_health_missing_ref_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_verification_artifacts([{"type": "deploy_health", "sha256": "a" * 64}])
    assert exc.value.exit_code == 2


def test_screenshot_missing_ref_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_verification_artifacts([{"type": "screenshot", "sha256": "a" * 64}])
    assert exc.value.exit_code == 2


def test_empty_artifacts_exit_24() -> None:
    body = _minimal_body(artifacts=[])
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verification_evidence", body=body)
    assert exc.value.exit_code == 24


def test_non_verifier_actor_exit_23() -> None:
    body = _minimal_body(actor_role="producer")
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verification_evidence", body=body)
    assert exc.value.exit_code == 23


def test_bad_bv_verdict_exit_2() -> None:
    body = _minimal_body(bv_verdict="PASS")
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verification_evidence", body=body)
    assert exc.value.exit_code == 2


def test_round_less_than_one_exit_2() -> None:
    body = _minimal_body(round=0)
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="verification_evidence", body=body)
    assert exc.value.exit_code == 2


def test_genesis_forbids_verification_evidence_keys() -> None:
    for key in ("phase_id", "frozen_spec", "round", "bv_verdict", "artifacts", "subject_sha256"):
        with pytest.raises(EntryValidationError) as exc:
            validate_append_body(kind="genesis", body={key: "x"})
        assert exc.value.exit_code == 2


def test_frozen_spec_opaque_without_file_existence() -> None:
    body = _minimal_body(frozen_spec="docs/DOES-NOT-EXIST.md")
    validated = validate_append_body(kind="verification_evidence", body=body)
    assert validated["frozen_spec"] == "docs/DOES-NOT-EXIST.md"


def test_require_verification_evidence_config_parse(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    assert "require_verification_evidence" not in data["honesty"]
    config = load_config(cfg_path)
    assert config.honesty.require_verification_evidence == "off"

    for mode in ("off", "warn", "require"):
        data["honesty"]["require_verification_evidence"] = mode
        cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
        assert load_config(cfg_path).honesty.require_verification_evidence == mode

    data["honesty"]["require_verification_evidence"] = "maybe"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(Exception, match="require_verification_evidence"):
        load_config(cfg_path)


def test_require_verification_evidence_in_honesty_keys() -> None:
    assert "require_verification_evidence" in HONESTY_KEYS


def test_honesty_error_token_includes_missing_verification_evidence() -> None:
    from typing import get_args

    from tools.honesty.types import HonestyErrorToken

    assert "missing_verification_evidence" in get_args(HonestyErrorToken)

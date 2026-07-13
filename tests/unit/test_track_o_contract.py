"""Unit tests — Track O product-contract parse/presence helpers (§O0.8 unit)."""

from __future__ import annotations

from pathlib import Path

from tools.track_o.validate import (
    ABS_MACHINE_PATH_RE,
    MINIMAL_VALID_CONTRACT,
    SECRET_ASSIGNMENT_RE,
    STAGE_LABELS,
    check_deferred_ceremony,
    check_no_abs_machine_paths,
    check_no_secret_patterns,
    check_rejection_keywords,
    check_stage_labels,
    validate_contract_fixture,
    validate_contract_text,
    ValidationResult,
)

KIT_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = KIT_ROOT / "docs" / "TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md"


def test_stage_labels_include_four_normie_stages() -> None:
    assert STAGE_LABELS[0].endswith("Start")
    assert "Work" in STAGE_LABELS[1]
    assert "GitHub backup" in STAGE_LABELS[2]
    assert "Knowtation bind" in STAGE_LABELS[3]


def test_minimal_fixture_passes_unit_checks() -> None:
    result = validate_contract_fixture(MINIMAL_VALID_CONTRACT)
    assert result.ok, result.errors


def test_real_contract_has_required_stage_labels() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    result = ValidationResult(ok=True)
    check_stage_labels(text, result)
    assert result.ok, result.errors


def test_real_contract_has_deferred_ceremony_keywords() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    result = ValidationResult(ok=True)
    check_deferred_ceremony(text, result)
    assert result.ok, result.errors


def test_real_contract_has_rejection_keywords() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    result = ValidationResult(ok=True)
    check_rejection_keywords(text, result)
    assert result.ok, result.errors


def test_real_contract_no_abs_machine_paths() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    result = ValidationResult(ok=True)
    check_no_abs_machine_paths(text, result, label="contract")
    assert result.ok, result.errors
    assert not ABS_MACHINE_PATH_RE.search(text)


def test_real_contract_no_secret_assignment_patterns() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    result = ValidationResult(ok=True)
    check_no_secret_patterns(text, result, label="contract")
    assert result.ok, result.errors
    assert not SECRET_ASSIGNMENT_RE.search(text)


def test_missing_stage_fails_closed() -> None:
    bad = MINIMAL_VALID_CONTRACT.replace("### Stage 4 — Optional Knowtation bind", "### Stage X")
    result = ValidationResult(ok=True)
    validate_contract_text(bad, result)
    assert not result.ok
    assert any(e.startswith("missing_stage:") for e in result.errors)

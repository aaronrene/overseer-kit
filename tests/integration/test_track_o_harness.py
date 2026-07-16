"""Integration tests — Track O harness on fixture contract docs (§O0.8 integration)."""

from __future__ import annotations

from tools.track_o.validate import MINIMAL_VALID_CONTRACT, validate_contract_fixture


def test_valid_fixture_ok() -> None:
    result = validate_contract_fixture(MINIMAL_VALID_CONTRACT)
    assert result.ok, result.errors


def test_missing_stage3_heading_fails_closed() -> None:
    bad = MINIMAL_VALID_CONTRACT.replace(
        "### Stage 3 — Optional GitHub backup",
        "### Stage Three — Backup later",
    )
    result = validate_contract_fixture(bad)
    assert not result.ok
    assert any("missing_stage" in e for e in result.errors)


def test_missing_stage4_heading_fails_closed() -> None:
    bad = MINIMAL_VALID_CONTRACT.replace(
        "### Stage 4 — Optional Knowtation bind",
        "### Optional vault",
    )
    result = validate_contract_fixture(bad)
    assert not result.ok
    assert any("missing_stage" in e for e in result.errors)


def test_mutated_boundary_missing_kit_owns_fails_closed() -> None:
    bad = MINIMAL_VALID_CONTRACT.replace(
        "`ok init` / regimes / adapters | **Owns**",
        "regimes | Consumes",
    )
    result = validate_contract_fixture(bad)
    assert not result.ok
    assert any("missing_boundary" in e for e in result.errors)


def test_stage3_one_click_shipped_claim_fails_closed() -> None:
    bad = (
        MINIMAL_VALID_CONTRACT
        + "\n\nStage 3 one-click backup is shipped and available without O2.\n"
    )
    result = validate_contract_fixture(bad)
    assert not result.ok
    assert any("one_click_shipped" in e for e in result.errors)

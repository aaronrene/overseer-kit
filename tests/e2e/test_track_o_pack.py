"""E2E — real Track O contract pack paths (§O0.8 e2e)."""

from __future__ import annotations

from pathlib import Path

from tools.track_o.validate import (
    CONTRACT_REL,
    KNOWTATION_REL,
    SCOOLING_REL,
    validate_track_o_pack,
)

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_real_pack_paths_resolve() -> None:
    assert (KIT_ROOT / CONTRACT_REL).is_file()
    assert (KIT_ROOT / SCOOLING_REL).is_file()
    assert (KIT_ROOT / KNOWTATION_REL).is_file()


def test_validate_track_o_pack_on_kit_root_passes() -> None:
    result = validate_track_o_pack(KIT_ROOT)
    assert result.ok, result.errors


def test_scooling_and_knowtation_remain_operator_gated() -> None:
    scooling = (KIT_ROOT / SCOOLING_REL).read_text(encoding="utf-8")
    knowtation = (KIT_ROOT / KNOWTATION_REL).read_text(encoding="utf-8")
    assert "operator-gated" in scooling
    assert "operator-gated" in knowtation
    assert "no live" in knowtation.lower()


def test_track_o_does_not_claim_scooling_mandatory() -> None:
    contract = (KIT_ROOT / CONTRACT_REL).read_text(encoding="utf-8")
    scooling = (KIT_ROOT / SCOOLING_REL).read_text(encoding="utf-8")
    assert "not** required" in contract or "not required" in contract.lower()
    assert "optional" in scooling.lower()
    assert "mandatory" not in contract.lower() or "not" in contract.lower()


def test_stage3_points_at_o2_and_upgrade_regime() -> None:
    contract = (KIT_ROOT / CONTRACT_REL).read_text(encoding="utf-8")
    scooling = (KIT_ROOT / SCOOLING_REL).read_text(encoding="utf-8")
    assert "ok upgrade-regime" in contract
    assert "PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY" in contract
    assert "deferred to Thinking O2" not in contract
    assert "deferred to O2" not in contract
    assert "deferred to O2" not in scooling
    assert "ok upgrade-regime" in scooling or "PHASE-TRACK-O-O2" in scooling
    assert "one-click" in contract.lower()
    # One-click still blocked until §O2.6
    assert "§O2.6" in contract or "O2.6" in contract

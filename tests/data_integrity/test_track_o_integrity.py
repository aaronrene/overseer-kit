"""Data-integrity — Track O harness idempotency and no rewrite (§O0.8 data-integrity)."""

from __future__ import annotations

from pathlib import Path

from tools.track_o.validate import CONTRACT_REL, validate_track_o_pack

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_harness_idempotent_same_verdict() -> None:
    r1 = validate_track_o_pack(KIT_ROOT)
    r2 = validate_track_o_pack(KIT_ROOT)
    assert r1.ok and r2.ok
    assert r1.errors == r2.errors == []


def test_contract_bytes_not_rewritten_by_harness() -> None:
    path = KIT_ROOT / CONTRACT_REL
    before = path.read_bytes()
    result = validate_track_o_pack(KIT_ROOT)
    after = path.read_bytes()
    assert result.ok, result.errors
    assert before == after


def test_no_partial_write_on_induced_failure(tmp_path: Path) -> None:
    """Missing pack under tmp_path fails closed without creating contract files."""
    # Seed only an empty docs tree — no contract.
    (tmp_path / "docs").mkdir()
    before = list(tmp_path.rglob("*"))
    result = validate_track_o_pack(tmp_path)
    after = list(tmp_path.rglob("*"))
    assert not result.ok
    assert any(e.startswith("missing_file:") for e in result.errors)
    assert before == after
    assert not (tmp_path / CONTRACT_REL).exists()

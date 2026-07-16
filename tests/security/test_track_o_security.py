"""Security tests — Track O contract pack (§O0.8 security)."""

from __future__ import annotations

import socket
from pathlib import Path
from unittest import mock

from tools.track_o.validate import (
    CONTRACT_REL,
    KNOWTATION_REL,
    MUSEHUB_OPTIONAL,
    PACK_RELS,
    SCOOLING_REL,
    SECRET_BLOB_PATTERNS,
    SILENT_REGIME_REJECTION,
    validate_track_o_pack,
)

KIT_ROOT = Path(__file__).resolve().parents[2]


def test_no_secret_patterns_in_contract_pack() -> None:
    for rel in PACK_RELS:
        text = (KIT_ROOT / rel).read_text(encoding="utf-8")
        for pattern in SECRET_BLOB_PATTERNS:
            assert not pattern.search(text), f"{rel} matched {pattern.pattern}"


def test_no_network_calls_on_harness_path() -> None:
    with mock.patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
        result = validate_track_o_pack(KIT_ROOT)
    assert result.ok, result.errors


def test_path_escape_outside_repo_root_fails_closed(tmp_path: Path) -> None:
    """A kit_root that cannot contain declared paths still fail-closes (missing files)."""
    alien = tmp_path / "alien"
    alien.mkdir()
    result = validate_track_o_pack(alien)
    assert not result.ok
    assert any(e.startswith("missing_file:") for e in result.errors)
    assert not (alien / CONTRACT_REL).exists()


def test_k7_musehub_optional_statement_present() -> None:
    text = (KIT_ROOT / CONTRACT_REL).read_text(encoding="utf-8")
    assert MUSEHUB_OPTIONAL in text


def test_silent_regime_edit_rejection_present() -> None:
    text = (KIT_ROOT / CONTRACT_REL).read_text(encoding="utf-8")
    assert SILENT_REGIME_REJECTION in text


def test_injected_secret_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "docs" / "consumers" / "scooling").mkdir(parents=True)
    (tmp_path / "docs" / "consumers" / "knowtation").mkdir(parents=True)
    contract = (KIT_ROOT / CONTRACT_REL).read_text(encoding="utf-8")
    poisoned = contract + '\napi_key = "sk-abcdefghijklmnopqrstuvwxyz1234567890"\n'
    (tmp_path / CONTRACT_REL).write_text(poisoned, encoding="utf-8")
    (tmp_path / SCOOLING_REL).write_text(
        (KIT_ROOT / SCOOLING_REL).read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / KNOWTATION_REL).write_text(
        (KIT_ROOT / KNOWTATION_REL).read_text(encoding="utf-8"), encoding="utf-8"
    )
    result = validate_track_o_pack(tmp_path)
    assert not result.ok
    assert any(e.startswith("secret_leak:") for e in result.errors)

"""Unit tests for ISR ledger kind + Mode D resolution (§ISR.11)."""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest
import yaml

from adapters.config import HONESTY_KEYS, HonestyConfig, load_config
from tests.fixtures.isr import load_isr_entry
from tests.support import seed_honesty_repo
from tools.honesty.status import HonestyStatusOptions, _resolve_mode
from tools.honesty.types import ENTRY_KINDS, ISR_VERDICTS, HonestyErrorToken
from tools.honesty.validate import (
    EntryValidationError,
    find_matching_independent_second_review,
    validate_append_body,
)


def _minimal(**overrides) -> dict:
    body = load_isr_entry("isr-pass.json")
    body.update(overrides)
    return body


def test_isr_in_entry_kinds() -> None:
    assert "independent_second_review" in ENTRY_KINDS
    assert ISR_VERDICTS == frozenset({"pass", "findings", "blocked"})


def test_validate_accepts_minimal_isr() -> None:
    validated = validate_append_body(kind="independent_second_review", body=_minimal())
    assert validated["kind"] == "independent_second_review"
    assert validated["isr_verdict"] == "pass"


def test_same_session_ids_exit_2() -> None:
    body = _minimal(actor_session_id="same", producer_session_id="same")
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="independent_second_review", body=body)
    assert exc.value.exit_code == 2


def test_empty_producer_session_exit_2() -> None:
    body = _minimal(producer_session_id="")
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="independent_second_review", body=body)
    assert exc.value.exit_code == 2


def test_missing_producer_session_exit_2() -> None:
    body = _minimal()
    del body["producer_session_id"]
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="independent_second_review", body=body)
    assert exc.value.exit_code == 2


def test_non_verifier_exit_23() -> None:
    body = _minimal(actor_role="producer")
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="independent_second_review", body=body)
    assert exc.value.exit_code == 23


def test_bad_isr_verdict_exit_2() -> None:
    body = _minimal(isr_verdict="ok")
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="independent_second_review", body=body)
    assert exc.value.exit_code == 2


def test_round_lt_1_exit_2() -> None:
    body = _minimal(round=0)
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="independent_second_review", body=body)
    assert exc.value.exit_code == 2


def test_both_agent_ids_equal_exit_2() -> None:
    body = _minimal(producer_agent_id="agent-x", verifier_agent_id="agent-x")
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="independent_second_review", body=body)
    assert exc.value.exit_code == 2


def test_one_agent_id_only_accept() -> None:
    validated = validate_append_body(
        kind="independent_second_review",
        body=_minimal(producer_agent_id="only-producer"),
    )
    assert validated["producer_agent_id"] == "only-producer"


def test_genesis_forbid_isr_keys() -> None:
    for key in (
        "isr_verdict",
        "producer_session_id",
        "producer_agent_id",
        "verifier_agent_id",
        "bound_verification_evidence_hash",
    ):
        with pytest.raises(EntryValidationError) as exc:
            validate_append_body(kind="genesis", body={key: "x"})
        assert exc.value.exit_code == 2


def test_frozen_spec_opaque_non_empty_no_must_exist() -> None:
    validated = validate_append_body(
        kind="independent_second_review",
        body=_minimal(frozen_spec="docs/does-not-need-to-exist.md"),
    )
    assert validated["frozen_spec"] == "docs/does-not-need-to-exist.md"


def test_require_isr_config_parse(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    assert "require_independent_second_reviewer" not in data["honesty"]
    config = load_config(cfg_path)
    assert config.honesty.require_independent_second_reviewer == "require"

    for mode in ("off", "warn", "require"):
        data["honesty"]["require_independent_second_reviewer"] = mode
        cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
        assert load_config(cfg_path).honesty.require_independent_second_reviewer == mode

    data["honesty"]["require_independent_second_reviewer"] = "maybe"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(Exception, match="require_independent_second_reviewer"):
        load_config(cfg_path)


def test_require_isr_in_honesty_keys() -> None:
    assert "require_independent_second_reviewer" in HONESTY_KEYS


def test_honesty_config_field_default_require() -> None:
    assert HonestyConfig().require_independent_second_reviewer == "require"


def test_error_token_includes_missing_isr() -> None:
    assert "missing_independent_second_review" in get_args(HonestyErrorToken)


def test_resolve_mode_d_invariants() -> None:
    # (1) Mode D + frozen-spec
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                independent_second_review="ISR-b",
                frozen_spec="docs/x.md",
            )
        )
        == "mode_d"
    )
    # (2) Mode D + producer-session
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                independent_second_review="ISR-b",
                producer_session="builder-chat-1",
            )
        )
        == "mode_d"
    )
    # (3) Mode D + both optionals
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                independent_second_review="ISR-b",
                producer_session="builder-chat-1",
                frozen_spec="docs/x.md",
            )
        )
        == "mode_d"
    )
    # (4) Mode D alone
    assert (
        _resolve_mode(
            HonestyStatusOptions(hook=None, artifact=None, independent_second_review="ISR-b")
        )
        == "mode_d"
    )
    # (5) producer alone → usage
    assert (
        _resolve_mode(HonestyStatusOptions(hook=None, artifact=None, producer_session="x"))
        is None
    )
    # (6) Mode B + producer → usage
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                verification_evidence="p",
                producer_session="x",
            )
        )
        is None
    )
    # (7) Mode C + producer → usage
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                deploy_health="p",
                producer_session="x",
            )
        )
        is None
    )
    # (8) Mode A + Mode D → usage
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook="board_done",
                artifact="a.txt",
                independent_second_review="ISR-b",
            )
        )
        is None
    )


def test_find_matching_isr_last_wins_and_pin() -> None:
    findings = load_isr_entry("isr-findings.json")
    findings["entry_hash"] = "f" * 64
    first_pass = load_isr_entry("isr-pass.json")
    first_pass["entry_hash"] = "a" * 64
    first_pass["round"] = 1
    second_pass = load_isr_entry("isr-pass.json")
    second_pass["entry_hash"] = "b" * 64
    second_pass["round"] = 2
    second_pass["actor_session_id"] = "verifier-chat-3"
    entries = [findings, first_pass, second_pass]

    assert (
        find_matching_independent_second_review(
            entries, phase_id="ISR-b", frozen_spec=None, producer_session=None
        )["entry_hash"]
        == "b" * 64
    )
    assert (
        find_matching_independent_second_review(
            [findings], phase_id="ISR-b", frozen_spec=None, producer_session=None
        )
        is None
    )
    pinned = find_matching_independent_second_review(
        entries,
        phase_id="ISR-b",
        frozen_spec=None,
        producer_session="builder-chat-1",
    )
    assert pinned is not None
    assert (
        find_matching_independent_second_review(
            entries,
            phase_id="ISR-b",
            frozen_spec=None,
            producer_session="other-builder",
        )
        is None
    )

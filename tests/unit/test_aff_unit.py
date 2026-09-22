"""Unit tests for AFF ledger kind + Mode E resolution (§AFF.14)."""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest
import yaml

from adapters.config import ADVERSARIAL_FREEZE_MODES, HONESTY_KEYS, HonestyConfig, load_config
from tests.fixtures.aff import AFF_DIGEST_PLACEHOLDER, AFF_FREEZE_REL, aff_body, load_aff_entry
from tests.support import seed_honesty_repo
from tools.adversarial_freeze import (
    aff_hold_bypassed,
    aggregate_adversarial_authorization_states,
    author_loop_complete,
    frv_authorizing_freeze_paths,
)
from tools.honesty.ledger import verify_chain
from tools.honesty.status import HonestyStatusOptions, _resolve_mode
from tools.honesty.types import AFF_POSTURES, AFF_VERDICTS, ENTRY_KINDS, HonestyErrorToken
from tools.honesty.validate import (
    EntryValidationError,
    find_latest_adversarial_freeze_verdict,
    find_matching_adversarial_freeze_pass,
    find_matching_adversarial_freeze_skip,
    validate_append_body,
)


def _minimal(**overrides) -> dict:
    body = load_aff_entry("aff-pass.json")
    body.update(overrides)
    return body


def test_aff_in_entry_kinds() -> None:
    assert "adversarial_freeze" in ENTRY_KINDS
    assert AFF_VERDICTS == frozenset({"pass", "findings", "blocked", "skip"})
    assert AFF_POSTURES == frozenset({"attack"})


@pytest.mark.parametrize(
    "fixture",
    ["aff-pass.json", "aff-findings.json", "aff-blocked.json"],
)
def test_validate_accepts_minimal_pass_findings_blocked(fixture: str) -> None:
    validated = validate_append_body(kind="adversarial_freeze", body=load_aff_entry(fixture))
    assert validated["kind"] == "adversarial_freeze"
    assert validated["aff_posture"] == "attack"
    assert validated["reviewer_model"] == "thinking-high"
    assert validated["producer_session_id"] == "aff-a-author-session"
    assert validated["actor_session_id"] != validated["producer_session_id"]


def test_validate_accepts_minimal_skip() -> None:
    validated = validate_append_body(kind="adversarial_freeze", body=load_aff_entry("aff-skip.json"))
    assert validated["aff_verdict"] == "skip"
    assert "aff_posture" not in validated


def test_client_v_true_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(v=True))
    assert exc.value.exit_code == 2


@pytest.mark.parametrize("bad_v", [0, 2, -1, 1.0, "1"])
def test_client_v_not_exact_one_exit_2(bad_v) -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(v=bad_v))
    assert exc.value.exit_code == 2


def test_supplied_empty_ts_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(ts=""))
    assert exc.value.exit_code == 2


def test_supplied_non_string_ts_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(ts=123))
    assert exc.value.exit_code == 2


def test_omitted_ts_accepted_for_server_fill() -> None:
    body = _minimal()
    body.pop("ts", None)
    validated = validate_append_body(kind="adversarial_freeze", body=body)
    assert "ts" not in validated or validated.get("ts")


def test_verify_chain_rejects_missing_ts() -> None:
    entry = {
        "v": 1,
        "kind": "genesis",
        "prev_hash": "0" * 64,
        "entry_hash": "1" * 64,
    }
    assert verify_chain([entry]) == 22


def test_verify_chain_rejects_v_true() -> None:
    from tools.honesty.canonical import compute_entry_hash
    from tools.honesty.genesis import GENESIS_PREV

    entry = {"v": True, "ts": "2026-01-01T00:00:00Z", "kind": "genesis", "prev_hash": GENESIS_PREV}
    entry["entry_hash"] = compute_entry_hash(entry)
    assert verify_chain([entry]) == 22


@pytest.mark.parametrize(
    "kind,extra",
    [
        (
            "verification_evidence",
            {
                "bv_verdict": "pass",
                "artifacts": [{"type": "test_output", "sha256": "b" * 64}],
            },
        ),
        (
            "independent_second_review",
            {"isr_verdict": "pass", "producer_session_id": "p"},
        ),
        (
            "freeze_review",
            {
                "gate": "substantive",
                "freeze_verdict": "pass",
                "artifact_digest": AFF_DIGEST_PLACEHOLDER,
                "reviewer_model": "thinking-high",
            },
        ),
        ("adversarial_freeze", {"aff_verdict": "pass", "aff_posture": "attack",
                                "artifact_digest": AFF_DIGEST_PLACEHOLDER,
                                "producer_session_id": "p", "reviewer_model": "m"}),
    ],
)
def test_round_true_rejected_on_round_bearing_kinds(kind: str, extra: dict) -> None:
    body = {
        "actor_role": "verifier",
        "actor_session_id": "a",
        "phase_id": "X",
        "frozen_spec": "docs/x.md",
        "round": True,
        **extra,
    }
    if kind == "adversarial_freeze":
        body["actor_session_id"] = "a"
        body["producer_session_id"] = "p"
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind=kind, body=body)
    assert exc.value.exit_code == 2


def test_missing_reviewer_model_exit_2() -> None:
    body = _minimal()
    del body["reviewer_model"]
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=body)
    assert exc.value.exit_code == 2


def test_same_session_ids_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(
            kind="adversarial_freeze",
            body=_minimal(actor_session_id="same", producer_session_id="same"),
        )
    assert exc.value.exit_code == 2


def test_missing_producer_session_on_pass_exit_2() -> None:
    body = _minimal()
    del body["producer_session_id"]
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=body)
    assert exc.value.exit_code == 2


def test_missing_aff_posture_on_pass_exit_2() -> None:
    body = _minimal()
    del body["aff_posture"]
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=body)
    assert exc.value.exit_code == 2


def test_aff_posture_not_attack_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(aff_posture="defend"))
    assert exc.value.exit_code == 2


def test_skip_with_aff_posture_exit_2() -> None:
    body = load_aff_entry("aff-skip.json")
    body["aff_posture"] = "attack"
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=body)
    assert exc.value.exit_code == 2


def test_skip_non_owner_exit_23() -> None:
    body = load_aff_entry("aff-skip.json")
    body["actor_role"] = "verifier"
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=body)
    assert exc.value.exit_code == 23


def test_pass_non_verifier_exit_23() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(actor_role="producer"))
    assert exc.value.exit_code == 23


def test_bad_aff_verdict_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(aff_verdict="ok"))
    assert exc.value.exit_code == 2


def test_round_lt_1_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(round=0))
    assert exc.value.exit_code == 2


def test_round_non_int_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="adversarial_freeze", body=_minimal(round="1"))
    assert exc.value.exit_code == 2


def test_digest_not_sha256_hex_exit_2() -> None:
    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(
            kind="adversarial_freeze",
            body=_minimal(artifact_digest="sha256:ZZZZ"),
        )
    assert exc.value.exit_code == 2


def test_genesis_forbid_aff_keys() -> None:
    for key in ("aff_verdict", "aff_posture", "bound_freeze_review_hash", "side_check_path"):
        with pytest.raises(EntryValidationError) as exc:
            validate_append_body(kind="genesis", body={key: "x"})
        assert exc.value.exit_code == 2


def test_adversarial_freeze_config_parse(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": "human",
        "human_escalation": [],
    }
    for mode in ADVERSARIAL_FREEZE_MODES:
        data["honesty"]["adversarial_freeze"] = mode
        cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
        assert load_config(cfg_path).honesty.adversarial_freeze == mode

    data["honesty"]["adversarial_freeze"] = "maybe"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(Exception, match="adversarial_freeze"):
        load_config(cfg_path)


def test_derived_suggest_from_security(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"].pop("adversarial_freeze", None)
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": "human",
        "human_escalation": ["security"],
    }
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert load_config(cfg_path).honesty.adversarial_freeze == "suggest"


def test_derived_off_without_security(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"].pop("adversarial_freeze", None)
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": "human",
        "human_escalation": [],
    }
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert load_config(cfg_path).honesty.adversarial_freeze == "off"


def test_explicit_off_wins_over_security(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["adversarial_freeze"] = "off"
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": "human",
        "human_escalation": ["security"],
    }
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert load_config(cfg_path).honesty.adversarial_freeze == "off"


def test_require_never_derived(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"].pop("adversarial_freeze", None)
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": "human",
        "human_escalation": ["security"],
    }
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert load_config(cfg_path).honesty.adversarial_freeze != "require"


def test_adversarial_freeze_in_honesty_keys() -> None:
    assert "adversarial_freeze" in HONESTY_KEYS


def test_honesty_config_field_default_suggest() -> None:
    assert HonestyConfig().adversarial_freeze == "suggest"


def test_error_token_includes_missing_adversarial_freeze() -> None:
    assert "missing_adversarial_freeze" in get_args(HonestyErrorToken)


def test_resolve_mode_e_invariants() -> None:
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                frozen_spec="docs/x.md",
            )
        )
        == "mode_e"
    )
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                producer_session="author",
            )
        )
        == "mode_e"
    )
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                producer_session="author",
                frozen_spec="docs/x.md",
            )
        )
        == "mode_e"
    )
    assert (
        _resolve_mode(HonestyStatusOptions(hook=None, artifact=None, adversarial_freeze="AFF"))
        == "mode_e"
    )
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                frozen_spec="docs/x.md",
                artifact_digest=AFF_DIGEST_PLACEHOLDER,
            )
        )
        == "mode_e"
    )
    # digest without Mode E → usage
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                artifact_digest=AFF_DIGEST_PLACEHOLDER,
            )
        )
        is None
    )
    # Mode E + digest without frozen-spec → usage
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                artifact_digest=AFF_DIGEST_PLACEHOLDER,
            )
        )
        is None
    )
    # Mode E + Mode D → usage
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                independent_second_review="ISR-b",
            )
        )
        is None
    )
    # existing non-regular frozen-spec + valid digest still Mode E at resolve layer
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                frozen_spec="/tmp",  # path shape only; resolve_mode does not stat
                artifact_digest=AFF_DIGEST_PLACEHOLDER,
            )
        )
        == "mode_e"
    )


def _eligible_entries() -> list[dict]:
    digest = AFF_DIGEST_PLACEHOLDER
    path = AFF_FREEZE_REL
    pass1 = aff_body(artifact_digest=digest, round=1, entry_hash="p1" * 32)
    findings = aff_body(
        "aff-findings.json",
        artifact_digest=digest,
        round=2,
        actor_session_id="adv-3",
        entry_hash="f1" * 32,
    )
    blocked = aff_body(
        "aff-blocked.json",
        artifact_digest=digest,
        round=2,
        actor_session_id="adv-4",
        entry_hash="b1" * 32,
    )
    skip = aff_body(
        "aff-skip.json",
        artifact_digest=digest,
        round=2,
        entry_hash="s1" * 32,
    )
    return pass1, findings, blocked, skip, path, digest


def test_auto_hold_match_ignores_phase_id() -> None:
    pass1, _, _, _, path, digest = _eligible_entries()
    pass1["phase_id"] = "AFF"  # not AFF-b
    winner = find_matching_adversarial_freeze_pass(
        [pass1], frozen_spec=path, artifact_digest=digest, phase_id=None
    )
    assert winner is not None
    assert winner["phase_id"] == "AFF"


def test_mode_e_optional_phase_pin() -> None:
    pass1, _, _, _, path, digest = _eligible_entries()
    assert (
        find_latest_adversarial_freeze_verdict(
            [pass1], frozen_spec=path, artifact_digest=digest, phase_id="OTHER"
        )
        is None
    )
    assert (
        find_latest_adversarial_freeze_verdict(
            [pass1], frozen_spec=path, artifact_digest=digest, phase_id="AFF"
        )
        is not None
    )


def test_skip_match_ignores_producer_session() -> None:
    _, _, _, skip, path, digest = _eligible_entries()
    winner = find_matching_adversarial_freeze_skip(
        [skip], frozen_spec=path, artifact_digest=digest, phase_id=None
    )
    assert winner is not None
    # producer pin is ignored by skip wrapper (not passed through as filter on skip body)
    latest = find_latest_adversarial_freeze_verdict(
        [skip],
        frozen_spec=path,
        artifact_digest=digest,
        producer_session="ignored-author",
    )
    assert latest is not None
    assert latest["aff_verdict"] == "skip"


def test_pass_then_findings_never_returns_older_pass() -> None:
    pass1, findings, _, _, path, digest = _eligible_entries()
    assert (
        find_matching_adversarial_freeze_pass(
            [pass1, findings], frozen_spec=path, artifact_digest=digest
        )
        is None
    )
    latest = find_latest_adversarial_freeze_verdict(
        [pass1, findings], frozen_spec=path, artifact_digest=digest
    )
    assert latest is not None
    assert latest["aff_verdict"] == "findings"


def test_pass_then_blocked_never_returns_older_pass() -> None:
    pass1, _, blocked, _, path, digest = _eligible_entries()
    assert (
        find_matching_adversarial_freeze_pass(
            [pass1, blocked], frozen_spec=path, artifact_digest=digest
        )
        is None
    )


def test_pass_then_skip_never_returns_older_pass() -> None:
    pass1, _, _, skip, path, digest = _eligible_entries()
    assert (
        find_matching_adversarial_freeze_pass(
            [pass1, skip], frozen_spec=path, artifact_digest=digest
        )
        is None
    )
    assert (
        find_matching_adversarial_freeze_skip(
            [pass1, skip], frozen_spec=path, artifact_digest=digest
        )
        is not None
    )


def test_author_loop_complete_predicates() -> None:
    digest = AFF_DIGEST_PLACEHOLDER
    assert author_loop_complete("substantive", stamp_digest=None, current_digest=digest) is True
    assert (
        author_loop_complete("mechanical_only", stamp_digest=digest, current_digest=digest)
        is True
    )
    assert (
        author_loop_complete("mechanical_only", stamp_digest=None, current_digest=digest) is False
    )
    other = "sha256:" + ("b" * 64)
    assert (
        author_loop_complete("mechanical_only", stamp_digest=other, current_digest=digest) is False
    )
    assert author_loop_complete("absent", stamp_digest=digest, current_digest=digest) is False


def test_aff_hold_bypassed(repo_root: Path) -> None:
    from tests.fixtures.aff import seed_aff_repo

    cfg = seed_aff_repo(repo_root, adversarial_freeze="suggest", honesty_enabled=True)
    assert aff_hold_bypassed(cfg) is False
    cfg_off = seed_aff_repo(repo_root, adversarial_freeze="off", honesty_enabled=True)
    assert aff_hold_bypassed(cfg_off) is True
    cfg_dis = seed_aff_repo(repo_root, adversarial_freeze="suggest", honesty_enabled=False)
    assert aff_hold_bypassed(cfg_dis) is True
    cfg_req = seed_aff_repo(repo_root, adversarial_freeze="require", honesty_enabled=True)
    assert aff_hold_bypassed(cfg_req) is False


def test_helper_off_never_pending(repo_root: Path) -> None:
    from tests.fixtures.aff import seed_aff_repo
    from tools.adversarial_freeze import adversarial_authorization_state

    cfg = seed_aff_repo(repo_root, adversarial_freeze="off")
    auth = adversarial_authorization_state(repo_root, repo_root / AFF_FREEZE_REL, config=cfg)
    assert auth.state == "off"
    assert auth.state != "pending"


def test_resolver_eligibility_rejects_malformed() -> None:
    path = AFF_FREEZE_REL
    digest = AFF_DIGEST_PLACEHOLDER
    base = aff_body(artifact_digest=digest)

    empty_phase = {**base, "phase_id": ""}
    assert (
        find_latest_adversarial_freeze_verdict(
            [empty_phase], frozen_spec=path, artifact_digest=digest
        )
        is None
    )

    bool_round = {**base, "round": True}
    assert (
        find_latest_adversarial_freeze_verdict(
            [bool_round], frozen_spec=path, artifact_digest=digest
        )
        is None
    )

    no_model = {**base}
    del no_model["reviewer_model"]
    assert (
        find_latest_adversarial_freeze_verdict(
            [no_model], frozen_spec=path, artifact_digest=digest
        )
        is None
    )

    skip_bad_phase = aff_body("aff-skip.json", artifact_digest=digest, phase_id="")
    assert (
        find_latest_adversarial_freeze_verdict(
            [skip_bad_phase], frozen_spec=path, artifact_digest=digest
        )
        is None
    )


def test_frv_authorizing_freeze_paths_only_substantive(repo_root: Path) -> None:
    from tests.fixtures.aff import seed_aff_repo, write_mechanical_stamp
    from tools.honesty.ledger import append_entry
    from tools.honesty.types import LedgerAppendOptions

    cfg = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    path = repo_root / AFF_FREEZE_REL
    # mechanical only — not substantive
    only_mech = frv_authorizing_freeze_paths(
        repo_root, [path], phase_id="AFF-b", config=cfg
    )
    assert only_mech == []

    append_entry(
        config=cfg,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="freeze_review",
            body={
                "actor_role": "verifier",
                "actor_session_id": "frv-1",
                "phase_id": "AFF-b",
                "frozen_spec": AFF_FREEZE_REL,
                "round": 1,
                "gate": "substantive",
                "freeze_verdict": "pass",
                "artifact_digest": digest,
                "reviewer_model": "thinking-high",
            },
        ),
    )
    authorizing = frv_authorizing_freeze_paths(
        repo_root, [path], phase_id="AFF-b", config=cfg
    )
    assert authorizing == [path]


def test_aggregate_rank_absent_pending_skipped_pass() -> None:
    assert aggregate_adversarial_authorization_states(["pass", "pending"]) == "pending"
    assert aggregate_adversarial_authorization_states(["pass", "absent"]) == "absent"
    assert aggregate_adversarial_authorization_states(["skipped", "pass"]) == "skipped"
    assert aggregate_adversarial_authorization_states(["pass", "pass"]) == "pass"
    assert (
        aggregate_adversarial_authorization_states(["absent", "pending", "skipped", "pass"])
        == "absent"
    )

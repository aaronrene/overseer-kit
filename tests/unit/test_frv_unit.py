"""Unit tests for FRV freeze-review verdict integrity (§FRV.12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import load_config
from tools.freeze_authorization import ACCEPT_LEGACY_VERDICT_STAMP
from tools.freeze_authorization.resolve import (
    FreezeAuthorization,
    freeze_authorization_state,
    resolve_stamp_record,
)
from tools.freeze_reviewer.findings import derive_verdict
from tools.freeze_reviewer.providers.base import ApiReviewProvider, LocalReviewProvider
from tools.freeze_reviewer.stamp import build_stamp, merge_stamp_mapping
from tools.freeze_reviewer.types import Finding, ReviewStamp, ReviewerSettings, STAMP_KEY_ORDER
from tools.governance_hygiene.next_regen import (
    ADVISORY_FORGED_SUBSTANTIVE_GATE,
    ADVISORY_LEDGER_CHAIN_BROKEN,
    ADVISORY_MECHANICAL_ONLY,
    ADVISORY_OPERATOR_BLOCK,
    ADVISORY_OPERATOR_BLOCK_MALFORMED,
    ADVISORY_UNREADABLE_GATE,
    REASON_FREEZE_NOT_SUBSTANTIVE,
    compact_step_id,
)
from tools.honesty.types import ENTRY_KINDS, FREEZE_VERDICTS
from tools.honesty.validate import EntryValidationError, find_matching_freeze_review, validate_append_body


DIGEST = "sha256:" + ("a" * 64)


def _stamp_kwargs(**overrides):
    base = dict(
        reviewed_at="2026-09-12T00:00:00Z",
        mechanical_verdict="pass",
        reviewer_mode="agent",
        reviewer_model=None,
        reviewer_provider="local",
        kit_version="0.1.0",
        artifact_digest=DIGEST,
        gate="mechanical",
        produced_by="checklist_engine",
        provider_kind="rule_engine",
        checklist_ids=["C1", "C2"],
        checklist_source="builtin",
        findings_count=0,
        override_applied=False,
    )
    base.update(overrides)
    return base


def test_to_mapping_fourteen_keys_no_verdict() -> None:
    mapping = ReviewStamp(**_stamp_kwargs()).to_mapping()
    assert list(mapping.keys()) == list(STAMP_KEY_ORDER)
    assert len(mapping) == 14
    assert "verdict" not in mapping
    assert mapping["gate"] == "mechanical"


def test_mechanical_verdict_from_derive() -> None:
    assert derive_verdict([], human_escalation=["security"]) == "pass"
    findings = [
        Finding(check="C1", severity="MAJOR", category="completeness", path="a.md", line=1, message="x").with_citation()
    ]
    assert derive_verdict(findings, human_escalation=["security"]) == "findings"
    blockers = [
        Finding(check="C4", severity="BLOCKER", category="security", path="a.md", line=1, message="x").with_citation()
    ]
    assert derive_verdict(blockers, human_escalation=["security"]) == "blocked"


def test_resolver_six_branches() -> None:
    assert resolve_stamp_record({"gate": "mechanical", "mechanical_verdict": "pass"}).kind == "mechanical"
    forged = resolve_stamp_record({"gate": "substantive", "mechanical_verdict": "pass"})
    assert forged.kind == "forged_substantive"
    assert forged.advisory == "forged_substantive_gate"
    unread = resolve_stamp_record({"gate": 1})
    assert unread.kind == "unreadable"
    assert unread.advisory == "unreadable_gate"
    partial = resolve_stamp_record({"mechanical_verdict": "findings"})
    assert partial.kind == "mechanical"
    assert partial.verdict == "findings"
    assert ACCEPT_LEGACY_VERDICT_STAMP is True
    legacy = resolve_stamp_record({"verdict": "pass"})
    assert legacy.kind == "mechanical"
    assert legacy.verdict == "pass"
    assert resolve_stamp_record({}).kind == "none"
    assert resolve_stamp_record(None).kind == "none"


def test_producer_identity_four_pairs() -> None:
    local = LocalReviewProvider()
    assert local.producer_identity() == ("checklist_engine", "rule_engine")
    scripted = LocalReviewProvider(scripted_findings=[])
    assert scripted.producer_identity() == ("scripted_provider", "rule_engine")
    api_scripted = ApiReviewProvider(scripted_findings=[])
    assert api_scripted.producer_identity() == ("scripted_provider", "rule_engine")
    api = ApiReviewProvider()
    assert api.producer_identity() == ("api_model", "model_api")


def test_build_stamp_nulls_model_for_rule_engine(tmp_path: Path) -> None:
    path = tmp_path / "f.yaml"
    path.write_text("phase: X\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n", encoding="utf-8")
    from tools.freeze_reviewer.artifact import parse_artifact

    parsed = parse_artifact(path, rel_path="f.yaml")
    stamp = build_stamp(
        parsed,
        reviewer=ReviewerSettings("agent", "thinking-high", "local", "human"),
        kit_version="0.1.0",
        produced_by="checklist_engine",
        provider_kind="rule_engine",
        checklist_ids=["C1"],
        checklist_source="builtin",
        findings_count=0,
    )
    assert stamp.reviewer_model is None
    assert "verdict" not in stamp.to_mapping()
    api_stamp = build_stamp(
        parsed,
        reviewer=ReviewerSettings("agent", "thinking-high", "api", "human"),
        kit_version="0.1.0",
        produced_by="api_model",
        provider_kind="model_api",
        checklist_ids=["C1"],
        checklist_source="operator_file",
        findings_count=3,
    )
    assert api_stamp.reviewer_model == "thinking-high"
    assert api_stamp.checklist_source == "operator_file"
    assert api_stamp.findings_count == 3


def test_merge_keeps_unknown_drops_verdict() -> None:
    existing = {"verdict": "findings", "operator_note": "keep", "extra": {"nested": 1}}
    new = ReviewStamp(**_stamp_kwargs()).to_mapping()
    merged = merge_stamp_mapping(existing, new)
    assert "verdict" not in merged
    assert merged["operator_note"] == "keep"
    assert merged["extra"] == {"nested": 1}
    assert list(merged.keys())[:14] == list(STAMP_KEY_ORDER)


def test_freeze_review_entry_kind_and_validation() -> None:
    assert "freeze_review" in ENTRY_KINDS
    assert FREEZE_VERDICTS == frozenset({"pass", "findings", "blocked"})
    body = {
        "actor_role": "verifier",
        "actor_session_id": "review-1",
        "phase_id": "FRV-b",
        "frozen_spec": "docs/archive/phases/PHASE-FRV.md",
        "round": 1,
        "gate": "substantive",
        "freeze_verdict": "pass",
        "artifact_digest": DIGEST,
        "reviewer_model": "thinking-high",
    }
    assert validate_append_body(kind="freeze_review", body=body)["gate"] == "substantive"

    for bad in (
        {"gate": "mechanical"},
        {"freeze_verdict": "ok"},
        {"artifact_digest": "sha256:ABC"},
        {"artifact_digest": "sha256:" + ("a" * 63)},
        {"artifact_digest": "md5:" + ("a" * 64)},
        {"round": 0},
        {"round": "1"},
        {"phase_id": ""},
        {"frozen_spec": ""},
        {"findings_count": -1},
        {"checklist_ids": []},
        {"producer_session_id": "review-1"},
    ):
        mutated = dict(body)
        mutated.update(bad)
        with pytest.raises(EntryValidationError) as exc:
            validate_append_body(kind="freeze_review", body=mutated)
        assert exc.value.exit_code == 2

    with pytest.raises(EntryValidationError) as exc:
        validate_append_body(kind="freeze_review", body={**body, "actor_role": "producer"})
    assert exc.value.exit_code == 23

    for key in ("gate", "freeze_verdict", "artifact_digest", "checklist_ids", "findings_count"):
        with pytest.raises(EntryValidationError) as exc:
            validate_append_body(kind="genesis", body={key: "x"})
        assert exc.value.exit_code == 2


def test_find_matching_freeze_review_rules() -> None:
    good = {
        "kind": "freeze_review",
        "actor_role": "verifier",
        "gate": "substantive",
        "freeze_verdict": "pass",
        "phase_id": "FRV-b",
        "frozen_spec": "docs/x.md",
        "artifact_digest": DIGEST,
        "actor_session_id": "a",
        "entry_hash": "h1",
    }
    later = {**good, "entry_hash": "h2"}
    assert find_matching_freeze_review(
        [good, later], phase_id="FRV-b", frozen_spec="docs/x.md", artifact_digest=DIGEST
    )["entry_hash"] == "h2"
    assert (
        find_matching_freeze_review(
            [{**good, "freeze_verdict": "findings"}],
            phase_id="FRV-b",
            frozen_spec="docs/x.md",
            artifact_digest=DIGEST,
        )
        is None
    )
    assert (
        find_matching_freeze_review(
            [{**good, "gate": "mechanical"}],
            phase_id="FRV-b",
            frozen_spec="docs/x.md",
            artifact_digest=DIGEST,
        )
        is None
    )
    assert (
        find_matching_freeze_review(
            [good],
            phase_id="FRV-b",
            frozen_spec="docs/x.md",
            artifact_digest="sha256:" + ("b" * 64),
        )
        is None
    )
    same_session = {**good, "producer_session_id": "a"}
    assert (
        find_matching_freeze_review(
            [same_session], phase_id="FRV-b", frozen_spec="docs/x.md", artifact_digest=DIGEST
        )
        is None
    )


def test_advisory_and_reason_constants() -> None:
    assert REASON_FREEZE_NOT_SUBSTANTIVE == "freeze_not_substantive"
    assert ADVISORY_MECHANICAL_ONLY == "mechanical_only"
    assert ADVISORY_OPERATOR_BLOCK == "operator_block"
    assert ADVISORY_OPERATOR_BLOCK_MALFORMED == "operator_block_malformed"
    assert ADVISORY_LEDGER_CHAIN_BROKEN == "ledger_chain_broken"
    assert ADVISORY_FORGED_SUBSTANTIVE_GATE == "forged_substantive_gate"
    assert ADVISORY_UNREADABLE_GATE == "unreadable_gate"


def test_compact_step_id_retains_suffix() -> None:
    assert compact_step_id("**FRV-a Freeze**") == "FRV-a"
    assert compact_step_id("**FRV-b Build**") == "FRV-b"
    assert compact_step_id("**FRV-a Freeze**") != compact_step_id("**FRV-b Build**")


def test_freeze_authorization_states(tmp_path: Path) -> None:
    config = load_config(Path(__file__).resolve().parents[1] / "fixtures" / "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir()
    art = docs / "PHASE-FRV.md"
    art.write_text(
        "```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n"
        "review_stamp:\n  verdict: pass\n```\n",
        encoding="utf-8",
    )
    auth = freeze_authorization_state(tmp_path, art, phase_id="FRV-b", config=config)
    assert isinstance(auth, FreezeAuthorization)
    assert auth.state == "mechanical_only"

    art.write_text(
        "```yaml\nphase: FRV\nauto_may_start: false\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n"
        "review_stamp:\n  verdict: pass\n```\n",
        encoding="utf-8",
    )
    assert freeze_authorization_state(tmp_path, art, phase_id="FRV-b", config=config).state == "blocked_by_operator"

    art.write_text(
        "```yaml\nphase: FRV\nauto_may_start: maybe\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n```\n",
        encoding="utf-8",
    )
    blocked = freeze_authorization_state(tmp_path, art, phase_id="FRV-b", config=config)
    assert blocked.state == "blocked_by_operator"
    assert blocked.advisory == "operator_block_malformed"

    art.write_text(
        "```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n"
        "review_stamp:\n  verdict: findings\n```\n",
        encoding="utf-8",
    )
    assert freeze_authorization_state(tmp_path, art, phase_id="FRV-b", config=config).state == "non_pass"

    art.write_text("# no stamp\n", encoding="utf-8")
    assert freeze_authorization_state(tmp_path, art, phase_id="FRV-b", config=config).state == "absent"

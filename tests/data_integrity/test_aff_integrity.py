"""Data-integrity tests for AFF last-verdict + hash-consistent malformations (§AFF.14)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.fixtures.aff import (
    AFF_FREEZE_REL,
    aff_body,
    current_artifact_digest,
    seed_aff_repo,
    write_mechanical_stamp,
)
from tools.adversarial_freeze import adversarial_authorization_state
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.genesis import GENESIS_PREV, build_genesis_entry
from tools.honesty.ledger import append_entry, verify_chain, verify_ledger_file
from tools.honesty.ledger_io import read_ledger_entries, serialize_entry
from tools.honesty.status import (
    EXIT_MISSING_ADVERSARIAL_FREEZE,
    HonestyStatusOptions,
    run_honesty_status,
)
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import (
    find_latest_adversarial_freeze_verdict,
    find_matching_adversarial_freeze_pass,
    validate_append_body,
)
from tools.governance_hygiene.next_regen import plan_next_regen, render_paste_ready


def _write_ledger(repo_root: Path, entries: list[dict]) -> None:
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    lines = [serialize_entry(e) for e in entries]
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _chain_append(prev: dict, body: dict) -> dict:
    entry = dict(body)
    if "ts" not in entry:
        entry["ts"] = "2026-01-01T00:00:00Z"
    if "v" not in entry:
        entry["v"] = 1
    entry["prev_hash"] = prev["entry_hash"]
    entry["entry_hash"] = compute_entry_hash(entry)
    return entry


def test_last_verdict_matrix_uses_append_accepted_bodies(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    path = AFF_FREEZE_REL

    def append(name: str, **kw):
        body = aff_body(name, artifact_digest=digest, **kw)
        # prove validate accepts before append
        validate_append_body(kind="adversarial_freeze", body=body)
        assert (
            append_entry(
                config=config,
                repo_root=repo_root,
                options=LedgerAppendOptions(kind="adversarial_freeze", body=body),
            ).exit_code
            == 0
        )

    append("aff-pass.json", round=1, actor_session_id="adv-1")
    entries = read_ledger_entries(
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    )
    assert find_matching_adversarial_freeze_pass(
        entries, frozen_spec=path, artifact_digest=digest
    ) is not None

    # pass → findings = pending (older pass revoked)
    append("aff-findings.json", round=2, actor_session_id="adv-2")
    entries = read_ledger_entries(
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    )
    assert (
        find_matching_adversarial_freeze_pass(
            entries, frozen_spec=path, artifact_digest=digest
        )
        is None
    )
    latest = find_latest_adversarial_freeze_verdict(
        entries, frozen_spec=path, artifact_digest=digest
    )
    assert latest["aff_verdict"] == "findings"

    # findings → pass = pass
    append("aff-pass.json", round=3, actor_session_id="adv-3")
    entries = read_ledger_entries(
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    )
    assert (
        find_matching_adversarial_freeze_pass(
            entries, frozen_spec=path, artifact_digest=digest
        )
        is not None
    )

    # pass → blocked = pending
    append("aff-blocked.json", round=4, actor_session_id="adv-4")
    entries = read_ledger_entries(
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    )
    assert (
        find_matching_adversarial_freeze_pass(
            entries, frozen_spec=path, artifact_digest=digest
        )
        is None
    )

    # blocked → pass, then pass → skip under suggest
    append("aff-pass.json", round=5, actor_session_id="adv-5")
    append("aff-skip.json", round=6)
    entries = read_ledger_entries(
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    )
    latest = find_latest_adversarial_freeze_verdict(
        entries, frozen_spec=path, artifact_digest=digest
    )
    assert latest["aff_verdict"] == "skip"
    auth = adversarial_authorization_state(
        repo_root, repo_root / AFF_FREEZE_REL, config=config
    )
    assert auth.state == "skipped"

    # skip → findings = pending
    append("aff-findings.json", round=7, actor_session_id="adv-7")
    auth = adversarial_authorization_state(
        repo_root, repo_root / AFF_FREEZE_REL, config=config
    )
    assert auth.state == "pending"


def test_different_digest_path_do_not_revoke(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    other = "sha256:" + ("b" * 64)
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body(artifact_digest=digest, actor_session_id="a1"),
        ),
    )
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body(
                "aff-findings.json",
                artifact_digest=other,
                actor_session_id="a2",
                frozen_spec="docs/other.md",
            ),
        ),
    )
    entries = read_ledger_entries(
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    )
    assert (
        find_matching_adversarial_freeze_pass(
            entries, frozen_spec=AFF_FREEZE_REL, artifact_digest=digest
        )
        is not None
    )


def test_skip_digest_d_does_not_authorize_d_prime(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    other = "sha256:" + ("c" * 64)
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body("aff-skip.json", artifact_digest=digest),
        ),
    )
    entries = read_ledger_entries(
        repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    )
    assert (
        find_latest_adversarial_freeze_verdict(
            entries, frozen_spec=AFF_FREEZE_REL, artifact_digest=other
        )
        is None
    )


def test_ok_next_twice_identical_fence(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    write_mechanical_stamp(repo_root)
    roadmap = (
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        f"| **AFF-a** | Thinking | **NEXT** | `{AFF_FREEZE_REL}` |\n"
    )
    handover = "## NEXT SESSION — AFF-a\n\n| | |\n| **ID** | **AFF-a** |\n\n"
    d1 = plan_next_regen(
        roadmap_text=roadmap, handover_text=handover, config=config, repo_root=repo_root
    )
    d2 = plan_next_regen(
        roadmap_text=roadmap, handover_text=handover, config=config, repo_root=repo_root
    )
    assert render_paste_ready(decision=d1, config=config) == render_paste_ready(
        decision=d2, config=config
    )


def test_broken_ledger_absent_hold_never_auto(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)
    append_entry(
        config=config,
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
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.write_text(ledger.read_text(encoding="utf-8") + "{bad}\n", encoding="utf-8")

    auth = adversarial_authorization_state(
        repo_root, repo_root / AFF_FREEZE_REL, config=config
    )
    assert auth.state == "absent"

    roadmap = (
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        f"| **AFF-b** | Auto | **NEXT** | `{AFF_FREEZE_REL}` |\n"
    )
    decision = plan_next_regen(
        roadmap_text=roadmap,
        handover_text="## NEXT\n| **ID** | **AFF-b** |\n",
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model != "Auto"


def test_mode_e_tamper_integrity_exits(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body(artifact_digest=digest),
        ),
    )
    # mutate prev_hash
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    lines = ledger.read_text(encoding="utf-8").strip().splitlines()
    last = json.loads(lines[-1])
    last["prev_hash"] = "0" * 64
    lines[-1] = json.dumps(last, separators=(",", ":"), sort_keys=True)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result.exit_code == 22
    assert result.exit_code != 0


def test_hash_consistent_malformed_ineligible(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)
    genesis = build_genesis_entry("2026-01-01T00:00:00Z")

    def make_pass(**mut) -> dict:
        body = aff_body(artifact_digest=digest)
        body.update(mut)
        body["ts"] = "2026-01-01T00:00:01Z"
        body["v"] = 1
        return body

    cases = [
        make_pass(phase_id=""),
        make_pass(round=True),
        {k: v for k, v in make_pass().items() if k != "reviewer_model"},
        make_pass(phase_id="   "),
        make_pass(round=0),
    ]
    # ensure round:true retains envelope fields
    for body in cases:
        if "ts" not in body:
            body["ts"] = "2026-01-01T00:00:01Z"
        if "v" not in body:
            body["v"] = 1

    for body in cases:
        entry = _chain_append(genesis, body)
        assert verify_chain([genesis, entry]) == 0
        winner = find_latest_adversarial_freeze_verdict(
            [genesis, entry],
            frozen_spec=AFF_FREEZE_REL,
            artifact_digest=digest,
        )
        assert winner is None
        _write_ledger(repo_root, [genesis, entry])
        auth = adversarial_authorization_state(
            repo_root, repo_root / AFF_FREEZE_REL, config=config
        )
        assert auth.state in {"pending", "absent"}
        assert auth.matched_via != "pass"
        result = run_honesty_status(
            config=config,
            repo_root=repo_root,
            options=HonestyStatusOptions(
                hook=None,
                artifact=None,
                adversarial_freeze="AFF",
                frozen_spec=AFF_FREEZE_REL,
            ),
        )
        assert result.exit_code == EXIT_MISSING_ADVERSARIAL_FREEZE
        assert result.json_payload.adversarial_freeze["matched_via"] is None


def test_hash_consistent_missing_ts_and_v_true_fail_closed(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    genesis = build_genesis_entry("2026-01-01T00:00:00Z")

    # omit ts, recompute hash
    body = aff_body(artifact_digest=digest)
    body["v"] = 1
    body.pop("ts", None)
    entry = dict(body)
    entry["prev_hash"] = genesis["entry_hash"]
    entry["entry_hash"] = compute_entry_hash(entry)
    assert verify_chain([genesis, entry]) == 22
    _write_ledger(repo_root, [genesis, entry])
    auth = adversarial_authorization_state(
        repo_root, repo_root / AFF_FREEZE_REL, config=config
    )
    assert auth.state == "absent"
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result.exit_code == 22

    # v: true with matching hash
    body2 = aff_body(artifact_digest=digest, actor_session_id="adv-x")
    body2["v"] = True
    body2["ts"] = "2026-01-01T00:00:02Z"
    entry2 = dict(body2)
    entry2["prev_hash"] = genesis["entry_hash"]
    entry2["entry_hash"] = compute_entry_hash(entry2)
    assert verify_chain([genesis, entry2]) == 22
    _write_ledger(repo_root, [genesis, entry2])
    result2 = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result2.exit_code == 22

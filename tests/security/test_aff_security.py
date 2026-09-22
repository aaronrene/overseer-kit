"""Security tests for AFF fail-closed gates (§AFF.14)."""

from __future__ import annotations

import inspect
from pathlib import Path

from cli.kit_root import kit_root
from tests.fixtures.aff import (
    AFF_FREEZE_REL,
    aff_body,
    seed_aff_repo,
    write_mechanical_stamp,
)
from tools.adversarial_freeze import (
    adversarial_authorization_state,
    aff_hold_bypassed,
    author_loop_complete,
    build_adversarial_freeze_gate,
)
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.genesis import build_genesis_entry
from tools.honesty.ledger import append_entry, verify_chain
from tools.honesty.ledger_io import serialize_entry
from tools.honesty.status import (
    EXIT_MISSING_ADVERSARIAL_FREEZE,
    HonestyStatusOptions,
    run_honesty_status,
)
from tools.honesty.types import LedgerAppendOptions
from tools.honesty.validate import find_latest_adversarial_freeze_verdict
from tools.governance_hygiene.next_regen import (
    ADVISORY_ADVERSARIAL_FREEZE_PENDING,
    decide_split_emission,
    plan_next_regen,
)
from tools.governance_hygiene.types import QueueRow


def test_no_secret_key_url_in_skill_and_paste() -> None:
    skill = (
        kit_root()
        / "cursor"
        / "skills"
        / "adversarial-freeze-review"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "sk-" not in skill
    assert "BEGIN PRIVATE" not in skill
    assert "api_key" not in skill.lower()
    # placeholders only
    assert "<THIS_CHAT_SESSION_ID>" in skill or "actor_session_id" in skill


def test_freeze_review_loop_forbids_auto_may_start_true() -> None:
    skill = (
        kit_root() / "cursor" / "skills" / "freeze-review-loop" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "MUST NOT write, insert, or flip `auto_may_start` to `true`" in skill
    assert "MUST NOT write `auto_may_start` at all" in skill
    # must not instruct agents to enable the flag
    assert "set auto_may_start to true" not in skill.lower()
    assert "flip auto_may_start to true and" not in skill.lower()


def test_url_like_session_ids_opaque(repo_root) -> None:
    config = seed_aff_repo(repo_root)
    digest = write_mechanical_stamp(repo_root)
    body = aff_body(
        artifact_digest=digest,
        actor_session_id="https://evil.example/$(curl)",
        producer_session_id="file:///etc/passwd; rm -rf /",
        notes="https://example.com/hook?x=`id`",
    )
    assert (
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="adversarial_freeze", body=body),
        ).exit_code
        == 0
    )


def test_no_network_or_model_imports_on_aff_paths() -> None:
    import tools.adversarial_freeze.authorize as auth_mod
    import tools.adversarial_freeze.surface as surface_mod
    import tools.honesty.status as status_mod
    import tools.honesty.validate as validate_mod

    for module in (auth_mod, surface_mod, status_mod, validate_mod):
        source = inspect.getsource(module)
        assert "urllib" not in source
        assert "requests" not in source
        assert "httpx" not in source
        assert "openai" not in source
        assert "anthropic" not in source


def test_author_session_cannot_append_pass_equal_ids(repo_root) -> None:
    config = seed_aff_repo(repo_root)
    digest = write_mechanical_stamp(repo_root)
    body = aff_body(
        artifact_digest=digest,
        actor_session_id="same-session",
        producer_session_id="same-session",
    )
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="adversarial_freeze", body=body),
    )
    assert result.exit_code == 2


def test_mechanical_stamp_without_aff_holds_auto(repo_root) -> None:
    for mode in ("suggest", "require"):
        config = seed_aff_repo(repo_root, adversarial_freeze=mode)
        digest = write_mechanical_stamp(repo_root)
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(
                kind="freeze_review",
                body={
                    "actor_role": "verifier",
                    "actor_session_id": "same-as-author-would-be",
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
        assert decision.emit_model == "Thinking"
        assert decision.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING


def test_stale_mechanical_only_does_not_satisfy_trigger_b(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    write_mechanical_stamp(repo_root)
    art = repo_root / AFF_FREEZE_REL
    art.write_text(art.read_text(encoding="utf-8") + "\nstale\n", encoding="utf-8")
    # stamp digest now unequal to current
    from tools.freeze_reviewer.artifact import extract_existing_stamp, parse_artifact, artifact_digest

    parsed = parse_artifact(art, rel_path=AFF_FREEZE_REL)
    stamp = extract_existing_stamp(parsed)
    current = artifact_digest(parsed)
    assert stamp is not None
    assert stamp.get("artifact_digest") != current
    assert (
        author_loop_complete(
            "mechanical_only",
            stamp_digest=stamp.get("artifact_digest"),
            current_digest=current,
        )
        is False
    )
    decision = plan_next_regen(
        roadmap_text=(
            "# Roadmap\n\n## Build queue\n\n"
            "| Phase | Model | Status | Deliverable |\n"
            "| --- | --- | --- | --- |\n"
            f"| **AFF-a** | Thinking | **NEXT** | `{AFF_FREEZE_REL}` |\n"
        ),
        handover_text="## NEXT\n| **ID** | **AFF-a** |\n",
        config=config,
        repo_root=repo_root,
    )
    assert decision.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING


def test_hash_consistent_malformed_cannot_authorize(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)
    genesis = build_genesis_entry("2026-01-01T00:00:00Z")
    body = aff_body(artifact_digest=digest)
    body.pop("reviewer_model")
    body["ts"] = "2026-01-01T00:00:01Z"
    body["v"] = 1
    entry = dict(body)
    entry["prev_hash"] = genesis["entry_hash"]
    entry["entry_hash"] = compute_entry_hash(entry)
    assert verify_chain([genesis, entry]) == 0
    assert (
        find_latest_adversarial_freeze_verdict(
            [genesis, entry], frozen_spec=AFF_FREEZE_REL, artifact_digest=digest
        )
        is None
    )
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        serialize_entry(genesis) + "\n" + serialize_entry(entry) + "\n",
        encoding="utf-8",
    )
    auth = adversarial_authorization_state(
        repo_root, repo_root / AFF_FREEZE_REL, config=config
    )
    assert auth.state != "pass"


def test_helper_off_under_disabled_honesty_cannot_hold(repo_root) -> None:
    config = seed_aff_repo(
        repo_root, adversarial_freeze="suggest", honesty_enabled=False
    )
    assert aff_hold_bypassed(config) is True
    auth = adversarial_authorization_state(
        repo_root, repo_root / AFF_FREEZE_REL, config=config
    )
    assert auth.state == "off"
    gate = build_adversarial_freeze_gate(config, repo_root)
    assert gate.skipped is True


def test_mode_e_suggest_cannot_soften_integrity(repo_root) -> None:
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
    ledger = repo_root / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    text = ledger.read_text(encoding="utf-8")
    ledger.write_text(text.replace("thinking-high", "tampered-model", 1), encoding="utf-8")
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


def test_fail_closed_read_failure_suggest_surfaces_absent(repo_root) -> None:
    from unittest.mock import patch

    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
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
    ledger.write_text("not-json\n", encoding="utf-8")
    art = repo_root / AFF_FREEZE_REL
    with patch(
        "tools.adversarial_freeze.surface.frv_authorizing_freeze_paths",
        return_value=[art],
    ):
        gate = build_adversarial_freeze_gate(
            config,
            repo_root,
            handover_text="## NEXT\n| **ID** | **AFF-b** |\n",
            roadmap_text=(
                "# Roadmap\n\n## Build queue\n\n"
                "| Phase | Model | Status | Deliverable |\n"
                "| --- | --- | --- | --- |\n"
                f"| **AFF-b** | Auto | **WIP** | `{AFF_FREEZE_REL}` |\n"
            ),
        )
    assert gate.skipped is False
    assert gate.state == "absent"
    assert gate.ok is True
    assert gate.message is not None
    assert "unreadable" in gate.message

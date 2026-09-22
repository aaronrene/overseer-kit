"""E2E tests for AFF Trigger A / Trigger B (§AFF.14)."""

from __future__ import annotations

from pathlib import Path

import yaml

from adapters.config import load_config
from tests.fixtures.aff import (
    AFF_FREEZE_REL,
    aff_body,
    current_artifact_digest,
    seed_aff_repo,
    write_mechanical_stamp,
)
from tools.adversarial_freeze import adversarial_authorization_state
from tools.freeze_reviewer.artifact import artifact_digest, parse_artifact
from tools.governance_hygiene.next_regen import (
    ADVISORY_ADVERSARIAL_FREEZE_PENDING,
    ADVISORY_ADVERSARIAL_FREEZE_SKIP,
    ADVISORY_MECHANICAL_ONLY,
    decide_split_emission,
    plan_next_regen,
    render_next_session,
    render_paste_ready,
)
from tools.governance_hygiene.types import QueueRow
from tools.honesty.ledger import append_entry
from tools.honesty.types import LedgerAppendOptions

DELIVERABLE = f"`{AFF_FREEZE_REL}`"


def _roadmap_two_row(*, a_status: str = "**NEXT**", b_status: str = "QUEUED") -> str:
    return (
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        f"| **AFF-a Adversarial freeze author** | Thinking | {a_status} | {DELIVERABLE} |\n"
        f"| **AFF-b Adversarial freeze build** | Auto | {b_status} | {DELIVERABLE} |\n"
    )


def _roadmap_split(*, status: str = "**NEXT**") -> str:
    return (
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        f"| **AFF Adversarial freeze build** | Thinking → Auto | {status} | {DELIVERABLE} |\n"
    )


def _handover(phase: str = "AFF-a") -> str:
    return f"## NEXT SESSION — {phase}\n\n| | |\n| **ID** | **{phase}** |\n\n"


def _append_frv(config, repo_root: Path, *, phase_id: str, digest: str) -> None:
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="freeze_review",
            body={
                "actor_role": "verifier",
                "actor_session_id": "frv-chat",
                "phase_id": phase_id,
                "frozen_spec": AFF_FREEZE_REL,
                "round": 1,
                "gate": "substantive",
                "freeze_verdict": "pass",
                "artifact_digest": digest,
                "reviewer_model": "thinking-high",
            },
        ),
    )


def _append_aff_pass(config, repo_root: Path, *, digest: str, phase_id: str = "AFF") -> None:
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body(artifact_digest=digest, phase_id=phase_id),
        ),
    )


def test_aff_trigger_b_paste_has_frozen_attack_contract(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    write_mechanical_stamp(repo_root)
    decision = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Thinking"
    assert decision.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING
    paste = render_paste_ready(decision=decision, config=config)
    assert "adversarial" in paste.lower() or "attack" in paste.lower()
    assert "Model: Thinking" in paste
    assert "Posture: attack — try to kill the freeze; do not rubber-stamp close" in paste
    assert "try to kill the freeze" in paste
    assert "different chat from the author" in paste
    assert "If this is the author session, stop." in paste
    assert "Prefer a different model than the author" in paste
    assert AFF_FREEZE_REL in paste
    assert "path:line" in paste
    assert "aff_posture: attack" in paste
    assert "<AUTHOR_PRODUCER_SESSION_NONCE>" in paste
    assert "On findings/blocked: append that negative verdict" in paste
    assert "never omit a negative append" in paste
    assert "Under suggest, operator skip is a separate owner append" in paste
    # §AFF.7.2 exact no-key contract — reversed "holds a key" must fail.
    assert "The kit performs no model call and holds no key." in paste
    assert "The kit performs no model call and holds a key." not in paste
    assert "No merge to main." in paste

    # §AFF.7.2 pass instruction must emit the complete §AFF.5.2 field set
    # from the real render_paste_ready path (not a paraphrased stand-in).
    assert "final binding operation" in paste
    assert (
        "On pass: §AFF.5.2 fields only — actor_role: verifier,\n"
        "   actor_session_id: <THIS_CHAT_SESSION_ID>, phase_id, round,\n"
        "   reviewer_model, frozen_spec, artifact_digest,\n"
        "   aff_verdict: pass, aff_posture: attack, and\n"
        "   producer_session_id: <AUTHOR_PRODUCER_SESSION_NONCE>"
    ) in paste

    # §AFF.7.4's order is part of the freeze contract, not prose decoration.
    assert paste.index("1. Finish the review") < paste.index("2. Write the adversarial round")
    assert paste.index("2. Write the adversarial round") < paste.index("3. Run ok review")
    assert paste.index("3. Run ok review") < paste.index("4. If Auto requires FRV")
    assert paste.index("4. If Auto requires FRV") < paste.index("5. Append adversarial_freeze")
    assert paste.index("5. Append adversarial_freeze") < paste.index("6. Do not edit")

    # §AFF.7.2 also freezes render_next_session bytes (not only the paste fence).
    next_session = render_next_session(
        decision=decision,
        roadmap_text=_roadmap_two_row(),
        config=config,
        sync_date="2026-09-20",
    )
    assert "**Model:** Thinking" in next_session
    assert "### THE ONE NEXT STEP — **Model: Thinking**" in next_session
    assert (
        "Adversarial freeze review (attack posture) — different chat from "
        "the author; try to kill the freeze before Auto may start."
    ) in next_session
    assert "Auto build" not in next_session


def test_aff_thinking_to_auto_split_holds_and_releases_by_digest(repo_root: Path) -> None:
    """Exercise §AFF.14's split convention through Trigger B then Trigger A."""
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)

    # The open split emits its Thinking (-a) side, but a fresh stamp makes
    # Trigger B replace the author paste with the adversarial one.
    trigger_b = plan_next_regen(
        roadmap_text=_roadmap_split(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert trigger_b.emit_model == "Thinking"
    assert trigger_b.step_label == "AFF-a"
    assert trigger_b.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING

    # A digest-bound AFF pass releases Trigger B without promoting the still
    # open Thinking side to Auto.
    _append_aff_pass(config, repo_root, digest=digest, phase_id="AFF")
    released_b = plan_next_regen(
        roadmap_text=_roadmap_split(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert released_b.emit_model == "Thinking"
    assert released_b.step_label == "AFF-a"
    assert released_b.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING

    # A later negative verdict revokes that pass. Once FRV makes the split's
    # Auto (-b) side eligible, Trigger A must hold until a fresh matching pass.
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body("aff-findings.json", artifact_digest=digest, phase_id="AFF"),
        ),
    )
    _append_frv(config, repo_root, phase_id="AFF", digest=digest)
    trigger_a = plan_next_regen(
        roadmap_text=_roadmap_split(),
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert trigger_a.emit_model == "Thinking"
    assert trigger_a.step_label == "AFF-b"
    assert trigger_a.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING

    _append_aff_pass(config, repo_root, digest=digest, phase_id="AFF")
    released_a = plan_next_regen(
        roadmap_text=_roadmap_split(),
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert released_a.emit_model == "Auto"
    assert released_a.step_label == "AFF-b"
    assert released_a.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING


def test_post_stamp_mutation_returns_to_author_paste(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    write_mechanical_stamp(repo_root)
    art = repo_root / AFF_FREEZE_REL
    # mutate outside review_stamp
    text = art.read_text(encoding="utf-8")
    art.write_text(text + "\n# byte-edit\n", encoding="utf-8")

    decision = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Thinking"
    assert decision.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING
    # FRV mechanical_only or plain Thinking — not adversarial hold
    assert decision.advisory in {ADVISORY_MECHANICAL_ONLY, None} or (
        decision.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING
    )

    # Auto row must not emit Auto (FRV still requires substantive)
    auto_row = QueueRow(
        phase_label="**AFF-b**",
        model="Auto",
        status="**NEXT**",
        deliverable=DELIVERABLE,
        raw_line="",
    )
    emit, reason, _, _ = decide_split_emission(auto_row, repo_root, config=config)
    assert emit is None
    assert reason == "freeze_not_substantive"

    # restamp → Trigger B holds again
    write_mechanical_stamp(repo_root)
    decision2 = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision2.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING


def test_aff_pass_phase_id_aff_releases_trigger_b_and_a(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    _append_aff_pass(config, repo_root, digest=digest, phase_id="AFF")

    # Trigger B released → ordinary Thinking (mechanical_only advisory ok)
    decision = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Thinking"
    assert decision.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING

    # Trigger A: open AFF-b + FRV → same path+digest pass clears Auto
    digest2 = write_mechanical_stamp(repo_root)  # may change digest — rebind
    # after restamp digest changes; re-append AFF for new digest + FRV
    _append_frv(config, repo_root, phase_id="AFF-b", digest=digest2)
    # old AFF won't match new digest — append pass for new digest with phase AFF
    _append_aff_pass(config, repo_root, digest=digest2, phase_id="AFF")

    roadmap_b = _roadmap_two_row(a_status="**DONE**", b_status="**NEXT**")
    decision_b = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision_b.emit_model == "Auto"
    assert decision_b.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING


def test_section_aff_7_4_transaction(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)
    _append_frv(config, repo_root, phase_id="AFF-b", digest=digest)
    _append_aff_pass(config, repo_root, digest=digest, phase_id="AFF")

    roadmap_b = _roadmap_two_row(a_status="**DONE**", b_status="**NEXT**")
    decision = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Auto"

    # Review-record row (prose) invalidates digest — simulate by body edit
    art = repo_root / AFF_FREEZE_REL
    art.write_text(art.read_text(encoding="utf-8") + "\n| AFF-ADV-rX | pass |\n", encoding="utf-8")
    # restamp alone does not restore Auto (AFF/FRV digest stale)
    new_digest = write_mechanical_stamp(repo_root)
    decision2 = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision2.emit_model != "Auto" or decision2.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING

    # rebind FRV alone still leaves AFF pending
    _append_frv(config, repo_root, phase_id="AFF-b", digest=new_digest)
    decision3 = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision3.emit_model == "Thinking"
    assert decision3.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING

    # AFF last restores both
    _append_aff_pass(config, repo_root, digest=new_digest, phase_id="AFF")
    decision4 = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision4.emit_model == "Auto"

    # one-byte later edit withdraws Auto
    art.write_text(art.read_text(encoding="utf-8") + "x", encoding="utf-8")
    decision5 = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision5.emit_model != "Auto"


def test_suggest_skip_emits_auto_with_advisory(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = write_mechanical_stamp(repo_root)
    _append_frv(config, repo_root, phase_id="AFF-b", digest=digest)
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body("aff-skip.json", artifact_digest=digest),
        ),
    )
    roadmap_b = _roadmap_two_row(a_status="**DONE**", b_status="**NEXT**")
    decision = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Auto"
    assert decision.advisory == ADVISORY_ADVERSARIAL_FREEZE_SKIP


def test_off_emits_auto_immediately_after_frv(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="off")
    digest = write_mechanical_stamp(repo_root)
    _append_frv(config, repo_root, phase_id="AFF-b", digest=digest)
    roadmap_b = _roadmap_two_row(a_status="**DONE**", b_status="**NEXT**")
    decision = plan_next_regen(
        roadmap_text=roadmap_b,
        handover_text=_handover("AFF-b"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Auto"
    assert decision.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING


def _disabled_honesty_loops(repo_root: Path, *, explicit_suggest: bool) -> None:
    if explicit_suggest:
        config = seed_aff_repo(
            repo_root, adversarial_freeze="suggest", honesty_enabled=False
        )
    else:
        config = seed_aff_repo(
            repo_root,
            adversarial_freeze=None,
            omit_adversarial_freeze_key=True,
            honesty_enabled=False,
            human_escalation=["security"],
        )
    assert config.honesty.enabled is False

    write_mechanical_stamp(repo_root)
    # Trigger B: author freeze paste, not adversarial_freeze_pending
    decision = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.emit_model == "Thinking"
    assert decision.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING

    digest = current_artifact_digest(repo_root)
    # Trigger A with freeze candidates, no FRV → freeze_not_substantive (not AFF)
    auto_row = QueueRow(
        phase_label="**AFF-b**",
        model="Auto",
        status="**NEXT**",
        deliverable=DELIVERABLE,
        raw_line="",
    )
    emit, reason, _, adv = decide_split_emission(auto_row, repo_root, config=config)
    assert emit is None
    assert reason == "freeze_not_substantive"

    # with FRV substantive — Auto (AFF bypassed)
    _append_frv(config, repo_root, phase_id="AFF-b", digest=digest)
    # honesty disabled → append may refuse; write FRV by temporarily enabling
    # Actually append_entry refuses when honesty disabled. Seed FRV while enabled then disable.
    pass


def test_disabled_honesty_explicit_and_derived_suggest(repo_root: Path) -> None:
    # Append FRV while honesty enabled, then disable (ledger match skipped when off).
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest", honesty_enabled=True)
    write_mechanical_stamp(repo_root)

    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["enabled"] = False
    data["honesty"]["adversarial_freeze"] = "suggest"
    if "modules" in data and isinstance(data["modules"], dict):
        data["modules"].setdefault("honesty", {})["enabled"] = False
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg_path)

    # Trigger B: author freeze paste, not adversarial_freeze_pending
    decision_b = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision_b.emit_model == "Thinking"
    assert decision_b.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING

    # Trigger A with freeze candidates: FRV freeze_not_substantive (not AFF hold)
    # (honesty off → ledger FRV ignored; stamp alone is mechanical_only)
    auto_row = QueueRow(
        phase_label="**AFF-b**",
        model="Auto",
        status="**NEXT**",
        deliverable=DELIVERABLE,
        raw_line="",
    )
    emit, reason, _, adv = decide_split_emission(auto_row, repo_root, config=config)
    assert emit is None
    assert reason == "freeze_not_substantive"
    assert adv != ADVISORY_ADVERSARIAL_FREEZE_PENDING

    # Trigger A with no freeze candidates → Auto
    no_cand = QueueRow(
        phase_label="**OTHER-b**",
        model="Auto",
        status="**NEXT**",
        deliverable="no freeze cite",
        raw_line="",
    )
    emit2, reason2, _, _ = decide_split_emission(no_cand, repo_root, config=config)
    assert emit2 == "Auto"
    assert reason2 is None

    from tools.adversarial_freeze import build_adversarial_freeze_gate

    assert build_adversarial_freeze_gate(config, repo_root).skipped is True

    # derived-suggest shape (key absent + security) + disabled
    data["honesty"].pop("adversarial_freeze", None)
    data["honesty"]["enabled"] = False
    if "modules" in data and isinstance(data["modules"], dict):
        data["modules"].setdefault("honesty", {})["enabled"] = False
    data["freeze_contract"]["human_escalation"] = ["security"]
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config2 = load_config(cfg_path)
    decision2 = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config2,
        repo_root=repo_root,
    )
    assert decision2.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING
    assert build_adversarial_freeze_gate(config2, repo_root).skipped is True
    emit3, reason3, _, _ = decide_split_emission(no_cand, repo_root, config=config2)
    assert emit3 == "Auto"


def test_operator_plus_auto_unchanged(repo_root: Path) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    write_mechanical_stamp(repo_root)
    row = QueueRow(
        phase_label="**LAND**",
        model="Operator + Auto",
        status="**NEXT**",
        deliverable=DELIVERABLE,
        raw_line="",
    )
    emit, reason, is_b, advisory = decide_split_emission(row, repo_root, config=config)
    assert emit == "Operator + Auto"
    assert reason is None


def test_muse_regime_trigger_loop(repo_root: Path) -> None:
    config = seed_aff_repo(
        repo_root,
        adversarial_freeze="suggest",
        regime_config="config-muse-git-mirror.yaml",
    )
    digest = write_mechanical_stamp(repo_root)
    decision = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision.advisory == ADVISORY_ADVERSARIAL_FREEZE_PENDING
    _append_aff_pass(config, repo_root, digest=digest, phase_id="AFF")
    decision2 = plan_next_regen(
        roadmap_text=_roadmap_two_row(),
        handover_text=_handover("AFF-a"),
        config=config,
        repo_root=repo_root,
    )
    assert decision2.advisory != ADVISORY_ADVERSARIAL_FREEZE_PENDING
    auth = adversarial_authorization_state(repo_root, repo_root / AFF_FREEZE_REL, config=config)
    assert auth.state == "pass"

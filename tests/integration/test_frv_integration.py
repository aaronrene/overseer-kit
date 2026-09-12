"""Integration tests for FRV (§FRV.12)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    git_status_runner,
    pass_provider_factory,
    run_cli,
    seed_freeze_repo,
    seed_honesty_repo,
    write_config,
)
from tools.freeze_reviewer.artifact import artifact_digest, extract_existing_stamp, parse_artifact
from tools.freeze_reviewer.engine import EXIT_STAMP_ESCALATION_REFUSED
from tools.governance_gates.scan import scan_governance_gates
from tools.governance_hygiene.next_regen import (
    decide_split_emission,
    format_change_log_fragment,
    format_next_regen_token,
    plan_next_regen,
)
from tools.governance_hygiene.types import QueueRow
from adapters.config import load_config
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.types import LedgerAppendOptions


def _enable_freeze_and_honesty(repo: Path) -> None:
    seed_honesty_repo(repo)
    cfg = repo / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": "agent",
        "human_escalation": ["security"],
    }
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_review_writes_fourteen_key_stamp(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    code = run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0
    stamp = extract_existing_stamp(parse_artifact(artifact, rel_path=rel))
    assert stamp is not None
    assert stamp.get("gate") == "mechanical"
    assert "verdict" not in stamp
    assert stamp.get("mechanical_verdict") == "pass"
    assert stamp.get("reviewer_model") is None
    assert len([k for k in stamp if k != "verdict"]) >= 14


def test_rerun_idempotent(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    first = artifact.read_bytes()
    stamp1 = extract_existing_stamp(parse_artifact(artifact, rel_path=rel))
    code = run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0
    assert artifact.read_bytes() == first
    stamp2 = extract_existing_stamp(parse_artifact(artifact, rel_path=rel))
    assert stamp1["reviewed_at"] == stamp2["reviewed_at"]


def test_escalation_refused_exit_39(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    text = artifact.read_text(encoding="utf-8")
    text = text.replace("mechanical_verdict: pass", "mechanical_verdict: findings")
    artifact.write_text(text, encoding="utf-8")
    before = artifact.read_bytes()
    code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
        json_mode=True,
    )
    assert code == EXIT_STAMP_ESCALATION_REFUSED
    assert artifact.read_bytes() == before


def test_escalation_dry_run_and_no_stamp_exit_0(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    text = artifact.read_text(encoding="utf-8")
    artifact.write_text(text.replace("mechanical_verdict: pass", "mechanical_verdict: findings"), encoding="utf-8")
    for flags in (["--dry-run"], ["--no-stamp"], ["--dry-run", "--no-stamp"], []):
        if not flags:
            continue
        code = run_cli(
            ["review", "--freeze", rel, *flags, "--json"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            review_provider_factory=pass_provider_factory(),
            json_mode=True,
        )
        assert code == 0, flags


def test_override_non_pass_stamp(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    text = artifact.read_text(encoding="utf-8")
    artifact.write_text(text.replace("mechanical_verdict: pass", "mechanical_verdict: findings"), encoding="utf-8")
    code = run_cli(
        ["review", "--freeze", rel, "--override-non-pass-stamp"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0
    stamp = extract_existing_stamp(parse_artifact(artifact, rel_path=rel))
    assert stamp["mechanical_verdict"] == "pass"
    assert stamp["override_applied"] is True


def test_forged_substantive_normalized(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    text = artifact.read_text(encoding="utf-8")
    artifact.write_text(text.replace("gate: mechanical", "gate: substantive"), encoding="utf-8")
    code = run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 0
    stamp = extract_existing_stamp(parse_artifact(artifact, rel_path=rel))
    assert stamp["gate"] == "mechanical"


def test_escalate_force_pass_still_banned(tmp_path: Path) -> None:
    artifact = seed_freeze_repo(tmp_path)
    code = run_cli(
        ["review", "--freeze", artifact.relative_to(tmp_path).as_posix(), "--escalate-force-pass"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    assert code == 1


def test_ledger_append_freeze_review(tmp_path: Path) -> None:
    _enable_freeze_and_honesty(tmp_path)
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    body = {
        "actor_role": "verifier",
        "actor_session_id": "review-chat-1",
        "phase_id": "FRV-b",
        "frozen_spec": "docs/archive/phases/PHASE-FRV.md",
        "round": 1,
        "gate": "substantive",
        "freeze_verdict": "pass",
        "artifact_digest": "sha256:" + ("c" * 64),
        "reviewer_model": "thinking-high",
    }
    assert append_entry(
        config=config,
        repo_root=tmp_path,
        options=LedgerAppendOptions(kind="freeze_review", body=body),
    ).exit_code == 0
    assert verify_ledger_file(config=config, repo_root=tmp_path).exit_code == 0


def test_split_and_plain_auto_emission(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    art = docs / "PHASE-FRV.md"
    art.write_text(
        "# Freeze\n\n```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n"
        "review_stamp:\n  verdict: pass\n```\n",
        encoding="utf-8",
    )
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    split_row = QueueRow(
        phase_label="**FRV**",
        model="Thinking → Auto",
        status="**NEXT**",
        deliverable="docs/PHASE-FRV.md",
        raw_line="",
    )
    emit, reason, is_b, advisory = decide_split_emission(split_row, tmp_path, config=config)
    assert emit == "Thinking"
    assert reason is None
    assert advisory == "mechanical_only"

    auto_row = QueueRow(
        phase_label="**FRV-b**",
        model="Auto",
        status="**NEXT**",
        deliverable="docs/PHASE-FRV.md",
        raw_line="",
    )
    emit, reason, is_b, advisory = decide_split_emission(auto_row, tmp_path, config=config)
    assert emit is None
    assert reason == "freeze_not_substantive"

    no_art = QueueRow(
        phase_label="**OTHER-b**",
        model="Auto",
        status="**NEXT**",
        deliverable="no freeze here",
        raw_line="",
    )
    emit, reason, is_b, advisory = decide_split_emission(no_art, tmp_path, config=config)
    assert emit == "Auto"
    assert reason is None

    op_row = QueueRow(
        phase_label="**LAND**",
        model="Operator + Auto",
        status="**NEXT**",
        deliverable="docs/PHASE-FRV.md",
        raw_line="",
    )
    emit, reason, is_b, advisory = decide_split_emission(op_row, tmp_path, config=config)
    assert emit == "Operator + Auto"


def test_gate_scan_mechanical_vs_substantive(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    art = docs / "archive" / "phases"
    art.mkdir(parents=True)
    phase = art / "PHASE-FRV.md"
    phase.write_text(
        "```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n"
        "review_stamp:\n  verdict: pass\n```\n",
        encoding="utf-8",
    )
    roadmap = (
        "# Roadmap\n\n## Build queue\n\n| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        "| **FRV-b Build** | Auto | **WIP** | docs/archive/phases/PHASE-FRV.md |\n"
    )
    (docs / "ROADMAP.md").write_text(roadmap, encoding="utf-8")
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "| **ID** | **FRV-b Build** |\n", encoding="utf-8"
    )
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    # ensure gates remind
    if not getattr(config.governance_gates, "remind", True):
        pass
    result = scan_governance_gates(config, tmp_path, roadmap_text=roadmap, handover_text="| **ID** | **FRV-b Build** |\n")
    pending = [p for p in result.pending if p.gate_id == "freeze_review"]
    assert pending
    assert "mechanical_only" in pending[0].message

"""E2E tests for FRV authorization loop (§FRV.12)."""

from __future__ import annotations

from pathlib import Path

import yaml

from adapters.config import load_config
from tests.support import seed_honesty_repo, write_config
from tools.freeze_reviewer.artifact import artifact_digest, parse_artifact
from tools.governance_hygiene.next_regen import decide_split_emission
from tools.governance_hygiene.types import QueueRow
from tools.honesty.ledger import append_entry
from tools.honesty.types import LedgerAppendOptions


def _seed(repo: Path) -> None:
    seed_honesty_repo(repo)
    cfg = repo / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": {"mode": "agent", "model": "thinking-high", "provider": "local", "fallback": "human"},
        "human_escalation": ["security"],
    }
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    docs = repo / "docs"
    docs.mkdir(parents=True, exist_ok=True)


def test_two_row_convention_requires_ledger(tmp_path: Path) -> None:
    _seed(tmp_path)
    art = tmp_path / "docs" / "PHASE-FRV.md"
    body = (
        "# Freeze\n\n```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n"
        "review_stamp:\n  gate: mechanical\n  mechanical_verdict: pass\n"
        "  produced_by: checklist_engine\n  provider_kind: rule_engine\n"
        "  reviewer_mode: agent\n  reviewer_model: null\n  reviewer_provider: local\n"
        "  checklist_ids: [C1]\n  checklist_source: builtin\n  findings_count: 0\n"
        "  override_applied: false\n  kit_version: 0.1.0\n"
        "  artifact_digest: sha256:deadbeef\n```\n\nseven-tier matrix\nfile+line\n"
    )
    # Write without bogus digest — compute after parse
    art.write_text(
        "# Freeze\n\n```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n```\n\n"
        "Ground truth frozen: true. seven-tier matrix. file+line citation.\n",
        encoding="utf-8",
    )
    parsed = parse_artifact(art, rel_path="docs/PHASE-FRV.md")
    digest = artifact_digest(parsed)
    config = load_config(tmp_path / ".overseer" / "config.yaml")

    auto_row = QueueRow(
        phase_label="**FRV-b**",
        model="Auto",
        status="**NEXT**",
        deliverable="docs/PHASE-FRV.md",
        raw_line="",
    )
    emit, reason, _, _ = decide_split_emission(auto_row, tmp_path, config=config)
    assert reason == "freeze_not_substantive"

    append_entry(
        config=config,
        repo_root=tmp_path,
        options=LedgerAppendOptions(
            kind="freeze_review",
            body={
                "actor_role": "verifier",
                "actor_session_id": "review-1",
                "phase_id": "FRV-b",
                "frozen_spec": "docs/PHASE-FRV.md",
                "round": 1,
                "gate": "substantive",
                "freeze_verdict": "pass",
                "artifact_digest": digest,
                "reviewer_model": "thinking-high",
            },
        ),
    )
    emit, reason, _, _ = decide_split_emission(auto_row, tmp_path, config=config)
    assert emit == "Auto"
    assert reason is None

    # One-byte edit invalidates digest binding
    art.write_text(art.read_text(encoding="utf-8") + "x", encoding="utf-8")
    emit, reason, _, _ = decide_split_emission(auto_row, tmp_path, config=config)
    assert reason == "freeze_not_substantive"


def test_prose_bold_pass_never_authorizes(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "PHASE-PROSE.md").write_text(
        "# Review\n\n| Round | Verdict |\n| --- | --- |\n| 1 | **pass** |\n\nreviewed → pass\n",
        encoding="utf-8",
    )
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    row = QueueRow(
        phase_label="**PROSE**",
        model="Thinking → Auto",
        status="**NEXT**",
        deliverable="docs/PHASE-PROSE.md",
        raw_line="",
    )
    emit, reason, is_b, advisory = decide_split_emission(row, tmp_path, config=config)
    assert emit == "Thinking"
    assert is_b is False

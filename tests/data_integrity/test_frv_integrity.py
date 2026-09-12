"""Data-integrity tests for FRV (§FRV.12)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, pass_provider_factory, run_cli, write_config
from tools.freeze_reviewer.artifact import artifact_digest, extract_existing_stamp, parse_artifact
from tools.freeze_reviewer.serializer import dump_freeze_mapping, round_trip_stable
from tools.freeze_reviewer.stamp import merge_stamp_mapping
from tools.freeze_reviewer.types import ReviewStamp, STAMP_KEY_ORDER


DIGEST = "sha256:" + ("e" * 64)


def test_digest_stable_across_stamp_rewrite(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    target = tmp_path / "docs" / "freeze.md"
    target.parent.mkdir(parents=True)
    original = (FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8")
    target.write_text(original, encoding="utf-8")
    rel = "docs/freeze.md"
    before = artifact_digest(parse_artifact(target, rel_path=rel))
    run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    after = artifact_digest(parse_artifact(target, rel_path=rel))
    assert before == after


def test_unknown_keys_survive_restamp(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    target = tmp_path / "freeze.yaml"
    target.write_text((FIXTURES / "freeze-artifact.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    run_cli(
        ["review", "--freeze", "freeze.yaml"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    text = target.read_text(encoding="utf-8")
    # inject unknown key inside stamp
    text = text.replace("override_applied: false", "override_applied: false\n  operator_note: keep-me")
    target.write_text(text, encoding="utf-8")
    run_cli(
        ["review", "--freeze", "freeze.yaml"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=pass_provider_factory(),
    )
    stamp = extract_existing_stamp(parse_artifact(target, rel_path="freeze.yaml"))
    assert stamp.get("operator_note") == "keep-me"


def test_round_trip_fourteen_key() -> None:
    mapping = {
        "phase": "FRV",
        "outputs": [{"id": "a", "path": "docs/a.md", "frozen": True}],
        "review_stamp": {
            "gate": "mechanical",
            "reviewed_at": "2026-09-12T00:00:00Z",
            "mechanical_verdict": "pass",
            "produced_by": "checklist_engine",
            "provider_kind": "rule_engine",
            "reviewer_mode": "agent",
            "reviewer_model": None,
            "reviewer_provider": "local",
            "checklist_ids": ["C1"],
            "checklist_source": "builtin",
            "findings_count": 0,
            "override_applied": False,
            "kit_version": "0.1.0",
            "artifact_digest": DIGEST,
        },
    }
    assert round_trip_stable(mapping)
    dumped = dump_freeze_mapping(mapping)
    assert "review_stamp:" in dumped
    assert list(mapping["review_stamp"].keys()) == list(STAMP_KEY_ORDER)


def test_merge_drops_legacy_verdict() -> None:
    merged = merge_stamp_mapping(
        {"verdict": "pass", "keep": 1},
        ReviewStamp(
            reviewed_at="t",
            mechanical_verdict="pass",
            reviewer_mode="agent",
            reviewer_model=None,
            reviewer_provider="local",
            kit_version="0.1.0",
            artifact_digest=DIGEST,
        ).to_mapping(),
    )
    assert "verdict" not in merged
    assert merged["keep"] == 1

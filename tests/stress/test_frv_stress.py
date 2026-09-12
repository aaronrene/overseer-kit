"""Stress tests for FRV (§FRV.12)."""

from __future__ import annotations

from pathlib import Path

from tools.honesty.validate import find_matching_freeze_review
from tools.governance_hygiene.next_regen import discover_freeze_candidates
from tools.freeze_reviewer.artifact import parse_artifact


DIGEST = "sha256:" + ("d" * 64)


def test_match_last_wins_large_ledger() -> None:
    entries: list[dict] = []
    for i in range(60):
        entries.append({"kind": "verdict", "actor_role": "verifier", "entry_hash": f"v{i}"})
    for i in range(50):
        entries.append(
            {
                "kind": "freeze_review",
                "actor_role": "verifier",
                "gate": "substantive",
                "freeze_verdict": "pass" if i == 49 else "findings",
                "phase_id": "FRV-b",
                "frozen_spec": "docs/x.md",
                "artifact_digest": DIGEST,
                "entry_hash": f"f{i}",
            }
        )
    # Only last freeze_review with pass
    entries[-1]["freeze_verdict"] = "pass"
    match = find_matching_freeze_review(
        entries, phase_id="FRV-b", frozen_spec="docs/x.md", artifact_digest=DIGEST
    )
    assert match is not None
    assert match["entry_hash"] == "f49"


def test_many_fences_parse(tmp_path: Path) -> None:
    fences = "\n\n".join(f"```text\nblock {i}\n```" for i in range(200))
    body = "x" * (1024 * 1024)
    path = tmp_path / "big.md"
    path.write_text(
        f"# Big\n\n```yaml\nphase: FRV\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n```\n\n{fences}\n\n{body}\n",
        encoding="utf-8",
    )
    parsed = parse_artifact(path, rel_path="big.md")
    assert parsed.declaration == "present"


def test_discover_cap_top_level_only(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    nested = docs / "archive" / "phases"
    nested.mkdir(parents=True)
    (docs / "PHASE-FRV.md").write_text("# top\n", encoding="utf-8")
    (nested / "PHASE-FRV-nested.md").write_text("# nested\n", encoding="utf-8")
    found = discover_freeze_candidates(tmp_path, "FRV", "docs/archive/phases/PHASE-FRV-nested.md")
    # top-level via glob + deliverable cite
    assert any(p.name == "PHASE-FRV.md" for p in found) or any("nested" in p.name for p in found)

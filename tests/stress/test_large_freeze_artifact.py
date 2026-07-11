"""Stress tests for large freeze artifacts (§K5.12)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import findings_provider_factory, git_status_runner, run_cli, write_config
from tools.freeze_reviewer.findings import assign_finding_ids
from tools.freeze_reviewer.types import Finding


def _large_artifact(path: Path, sections: int = 200) -> None:
    lines = [
        "# Large freeze",
        "",
        "```yaml",
        "phase: stress",
        "outputs:",
        "  - id: out",
        "    path: docs/x.md",
        "    frozen: true",
        "frozen_inputs:",
    ]
    for index in range(sections):
        lines.append(f"  - id: in-{index}")
        lines.append(f"    path: docs/in-{index}.md")
    lines.extend(["```", "", "seven-tier test matrix", "file+line discipline"])
    for index in range(sections):
        lines.append(f"## Section {index}")
        lines.append(f"ground truth edge {index}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_large_artifact_stable_sort(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    artifact = tmp_path / "docs" / "BIG.md"
    artifact.parent.mkdir(parents=True)
    _large_artifact(artifact, sections=300)
    rel = artifact.relative_to(tmp_path).as_posix()
    findings = [
        Finding(check="C1", severity="MINOR", category="other", path=rel, line=i, message=f"m{i}").with_citation()
        for i in range(1, 150)
    ]
    assigned = assign_finding_ids(findings)
    assert assigned[0].id == "F1"
    assert assigned[-1].id == "F149"
    code = run_cli(
        ["review", "--freeze", rel],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=findings_provider_factory(findings),
    )
    assert code == 7

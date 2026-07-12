"""Stress tests for API freeze review on large artifacts (K11)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FakeHttpTransport, api_provider_factory, git_status_runner, run_cli, write_config


def test_large_artifact_api_review_stable(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    write_config(tmp_path, "config-api-reviewer.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    sections = [
        "# Large freeze artifact\n",
        "```yaml\nphase: K11-stress\noutputs:\n  - id: out\n    path: docs/X.md\n    frozen: true\n```\n",
        "\nseven-tier test matrix\n",
    ]
    sections.extend(f"\n## Section {index}\nfrozen: true reference\n" for index in range(400))
    artifact = docs / "LARGE-FREEZE.md"
    artifact.write_text("".join(sections), encoding="utf-8")
    rel = artifact.relative_to(tmp_path).as_posix()
    findings = [
        {
            "check": "C3",
            "severity": "MINOR",
            "category": "consistency",
            "path": rel,
            "line": 5,
            "message": f"nit {index}",
        }
        for index in range(50)
    ]
    transport = FakeHttpTransport(
        review_body=json.dumps({"findings": findings}).encode("utf-8"),
    )
    code = run_cli(
        ["review", "--freeze", rel, "--json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
        json_mode=True,
    )
    assert code == 7
    assert len(transport.calls) >= 2

"""Data-integrity tests for API freeze review responses (K11)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FakeHttpTransport, api_provider_factory, git_status_runner, run_cli, seed_freeze_repo
from tools.freeze_reviewer.findings import assign_finding_ids, stable_sort_findings
from tools.freeze_reviewer.providers.api_response import parse_review_response
from tools.freeze_reviewer.types import Finding


def test_api_findings_stable_sort_matches_engine(tmp_path: Path) -> None:
    rel = "docs/FREEZE.md"
    payload = json.dumps(
        {
            "findings": [
                {
                    "check": "C2",
                    "severity": "MAJOR",
                    "category": "completeness",
                    "path": rel,
                    "line": 10,
                    "message": "b",
                },
                {
                    "check": "C1",
                    "severity": "MAJOR",
                    "category": "completeness",
                    "path": rel,
                    "line": 1,
                    "message": "a",
                },
            ]
        }
    ).encode("utf-8")
    parsed = parse_review_response(payload, default_path=rel)
    assigned = assign_finding_ids(parsed)
    assert assigned[0].id == "F1"
    assert assigned[0].line == 1
    assert assigned[1].id == "F2"
    assert stable_sort_findings(parsed)[0].line == 1


def test_identical_api_inputs_identical_cli_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    review_body = json.dumps(
        {
            "findings": [
                {
                    "check": "C8",
                    "severity": "MINOR",
                    "category": "consistency",
                    "path": rel,
                    "line": 2,
                    "message": "Citation nit.",
                }
            ]
        }
    ).encode("utf-8")

    def run_once() -> str:
        import io
        from contextlib import redirect_stdout

        from cli.context import CliContext
        from cli.main import main
        from cli.output import OutputContext

        transport = FakeHttpTransport(review_body=review_body)
        buffer = io.StringIO()
        ctx = CliContext.create(
            runner=git_status_runner(),
            cwd=tmp_path,
            kit=kit_root(),
            output=OutputContext(json_mode=True),
            review_provider_factory=api_provider_factory(transport),
        )
        with redirect_stdout(buffer):
            main(["review", "--freeze", rel, "--dry-run", "--json"], ctx=ctx)
        payload = json.loads(buffer.getvalue())
        payload.pop("stamp", None)
        return json.dumps(payload, sort_keys=True)

    assert run_once() == run_once()

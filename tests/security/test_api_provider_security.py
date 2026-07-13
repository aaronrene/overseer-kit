"""Security tests for headless API freeze provider (K11)."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cli.context import CliContext
from cli.kit_root import kit_root
from cli.main import main
from cli.output import OutputContext
from tests.support import (
    FakeHttpTransport,
    api_provider_factory,
    git_status_runner,
    run_cli,
    seed_freeze_repo,
    write_config,
)


def test_api_key_not_leaked_in_request_headers(tmp_path: Path, monkeypatch) -> None:
    secret = "super-secret-api-key-value"
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", secret)
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    artifact = seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    rel = artifact.relative_to(tmp_path).as_posix()
    transport = FakeHttpTransport(review_body=json.dumps({"findings": []}).encode("utf-8"))
    buffer = io.StringIO()
    ctx = CliContext.create(
        runner=git_status_runner(),
        cwd=tmp_path,
        kit=kit_root(),
        output=OutputContext(json_mode=True),
        review_provider_factory=api_provider_factory(transport),
    )
    with redirect_stdout(buffer):
        code = main(["review", "--freeze", rel, "--json"], ctx=ctx)
    assert code == 0
    out = buffer.getvalue()
    assert secret not in out
    auth_headers = [call["headers"].get("Authorization", "") for call in transport.calls]
    assert auth_headers
    assert all(header.startswith("Bearer ") and secret in header for header in auth_headers)


def test_api_artifact_injection_no_shell(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    write_config(tmp_path, "config-api-reviewer.yaml")
    artifact = tmp_path / "docs" / "evil.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "# evil\n\n```yaml\nphase: x\noutputs:\n  - id: a\n    path: docs/a.md\n    frozen: true\n```\n\n$(rm -rf /)\n",
        encoding="utf-8",
    )
    transport = FakeHttpTransport(review_body=json.dumps({"findings": []}).encode("utf-8"))
    with patch("adapters.runner.subprocess.run") as mocked:
        code = run_cli(
            ["review", "--freeze", "docs/evil.md", "--provider", "api"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
            review_provider_factory=api_provider_factory(transport),
        )
        assert mocked.call_count == 0 or all("rm -rf" not in str(call) for call in mocked.call_args_list)
    assert code in {0, 7, 8}
    post_calls = [call for call in transport.calls if call["method"] == "POST"]
    assert post_calls
    body_text = post_calls[0]["body"].decode("utf-8")
    assert "rm -rf" in body_text
    assert "$(rm -rf /)" in body_text


def test_api_path_escape_refused(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "ci-key")
    monkeypatch.setenv("OVERSEER_REVIEW_API_URL", "https://review.example.com/v1")
    seed_freeze_repo(tmp_path, config_name="config-api-reviewer.yaml")
    transport = FakeHttpTransport()
    code = run_cli(
        ["review", "--freeze", "../outside.md", "--provider", "api"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        review_provider_factory=api_provider_factory(transport),
    )
    assert code == 4
    assert transport.calls == []

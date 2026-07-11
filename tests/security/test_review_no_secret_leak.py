"""Security tests — no secret/path leak in review output (§K5.12)."""

from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

from cli.context import CliContext
from cli.kit_root import kit_root
from cli.main import main
from cli.output import OutputContext
from tests.support import git_status_runner, pass_provider_factory, seed_freeze_repo


def test_api_key_not_in_output(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OVERSEER_REVIEW_API_KEY", "super-secret-key-value")
    artifact = seed_freeze_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    buffer = io.StringIO()
    ctx = CliContext.create(
        runner=git_status_runner(),
        cwd=tmp_path,
        kit=kit_root(),
        output=OutputContext(json_mode=True),
        review_provider_factory=pass_provider_factory(),
    )
    with redirect_stdout(buffer):
        code = main(["review", "--freeze", rel, "--json"], ctx=ctx)
    out = buffer.getvalue()
    assert code == 0
    assert "super-secret-key-value" not in out
    payload = json.loads(out)
    assert "/" + tmp_path.name not in json.dumps(payload)

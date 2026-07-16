"""Unit tests for Track Q / Q1 overseer app (§Q0.12)."""

from __future__ import annotations

import json
from argparse import Namespace

import pytest

from cli.context import CliContext
from cli.main import COMMANDS
from cli.output import OutputContext
from tools.app.auth import generate_csrf_token, generate_session_credential
from tools.app.bind import DEFAULT_PORT, port_is_available, validate_bind_address
from tools.app.cors import origin_allowed
from tools.app.engine import handle_governance_sync, handle_review_freeze
from tools.app.envelope import ApiEnvelope, bad_request


def test_app_registered_in_commands() -> None:
    assert "app" in COMMANDS


@pytest.mark.parametrize(
    ("bind", "expected"),
    [
        ("127.0.0.1", "127.0.0.1"),
        ("localhost", "127.0.0.1"),
        ("::1", "::1"),
        ("0.0.0.0", None),
        ("::", None),
        ("192.168.1.1", None),
    ],
)
def test_bind_allowlist(bind: str, expected: str | None) -> None:
    assert validate_bind_address(bind) == expected


def test_default_port_constant() -> None:
    assert DEFAULT_PORT == 8765


def test_session_and_csrf_entropy() -> None:
    session = generate_session_credential()
    csrf = generate_csrf_token()
    assert len(session) >= 32
    assert len(csrf) >= 32


def test_envelope_json_roundtrip() -> None:
    env = ApiEnvelope(ok=True, exit_code=0, error=None, result={"x": 1})
    parsed = json.loads(env.to_json_bytes().decode("utf-8"))
    assert parsed["ok"] is True
    assert parsed["exit_code"] == 0


def test_unknown_post_keys_rejected() -> None:
    ctx = CliContext.create(output=OutputContext())
    result = handle_review_freeze(ctx, {"path": "docs/x.md", "extra": True})
    assert result.http_status == 400
    assert result.error == "unknown_fields"


def test_review_defaults_dry_run_true(tmp_path) -> None:
    from tests.fixtures.app import seed_app_repo

    seed_app_repo(tmp_path)
    ctx = CliContext.create(cwd=tmp_path, output=OutputContext())
    result = handle_review_freeze(ctx, {"path": "docs/ROADMAP.md"}, repo_arg=str(tmp_path))
    assert result.exit_code is not None


def test_governance_sync_defaults_non_write(tmp_path) -> None:
    from tests.fixtures.app import seed_app_repo
    from tests.support import make_runner, ok

    seed_app_repo(tmp_path)
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
            "git merge-base --is-ancestor": ok(""),
        }
    )
    ctx = CliContext.create(cwd=tmp_path, runner=runner, output=OutputContext())
    result = handle_governance_sync(ctx, {}, repo_arg=str(tmp_path))
    assert result.result is not None
    assert result.result.get("dry_run") is True


def test_bad_request_helper() -> None:
    env = bad_request("unknown_fields")
    assert env.http_status == 400


def test_cors_origin_allowlist() -> None:
    port = 8765
    assert origin_allowed(f"http://127.0.0.1:{port}", port)
    assert origin_allowed(f"http://localhost:{port}", port)
    assert origin_allowed(f"http://[::1]:{port}", port)
    assert not origin_allowed("http://evil.example:8765", port)


def test_occupied_default_port_reports_busy() -> None:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", DEFAULT_PORT))
        assert port_is_available("127.0.0.1", DEFAULT_PORT) is False

"""Security tests for the muse-sync hard gate (§KH2.8 security tier)."""

from __future__ import annotations

from pathlib import Path

from adapters.types import StatusResult
from tests.support import (
    FIXTURES,
    load_fixture_config,
    make_runner,
    ok,
    run_cli,
    seed_muse_substrate,
)
from tools.muse_sync import check_muse_sync


def test_fails_closed_when_dirty_state_unreadable(tmp_path: Path) -> None:
    """Rule §KH2.4: never optimistically report 'synced' when the flags could not be read."""
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    status = StatusResult(regime="muse+git-mirror", dirty=False, branch="main", muse_dirty=None, git_dirty=None)
    report = check_muse_sync(config, status)
    assert report.state == "unreadable"
    assert not report.ok


def test_remediation_text_is_a_static_string_never_shell_invoked(tmp_path: Path) -> None:
    """The remediation hint must be advisory text only — the kit never executes it."""
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    status = StatusResult(
        regime="muse+git-mirror", dirty=True, branch="main", muse_dirty=True, git_dirty=False
    )
    report = check_muse_sync(config, status)
    assert report.remediation == 'muse code add -A && muse commit -m "<message>"'
    # No shell metacharacter beyond the literal, static advisory string is ever built from
    # untrusted input — report.message/remediation never interpolate repo content.
    assert "$(" not in report.remediation
    assert "`" not in report.remediation


def test_muse_sync_payload_never_leaks_command_output_or_paths(tmp_path: Path) -> None:
    """The muse_sync report/payload carries only fixed enum-like state + static text — no
    raw command stdout, file paths, or secret-shaped values ever flow into it."""
    root = str(tmp_path.resolve())
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok(
                '{"dirty": true, "secret_token": "sk-should-never-surface-1234567890"}'
            ),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
        }
    )
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-muse-git-mirror.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    seed_muse_substrate(tmp_path)

    import json as _json
    from io import StringIO
    from unittest.mock import patch

    from cli.context import CliContext
    from cli.main import main
    from cli.output import OutputContext

    out = StringIO()
    with patch("sys.stdout", out):
        main(
            ["status", "--json"],
            ctx=CliContext.create(cwd=tmp_path, runner=runner, output=OutputContext(json_mode=True)),
        )
    payload = _json.loads(out.getvalue())
    assert "sk-should-never-surface" not in _json.dumps(payload["muse_sync"])
    assert set(payload["muse_sync"].keys()) == {"state", "ok", "remediation", "message"}


def test_review_freeze_refusal_does_not_run_review_provider(tmp_path: Path) -> None:
    """Least privilege: when muse_sync refuses, the freeze-review provider must never be invoked."""
    from cli.kit_root import kit_root
    from tests.support import findings_provider_factory, seed_freeze_repo

    root = str(tmp_path.resolve())
    artifact = seed_freeze_repo(tmp_path, config_name="config-muse-git-mirror.yaml")
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": true}'),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
        }
    )
    provider_calls: list[str] = []

    def _tracking_factory(name: str):
        provider_calls.append(name)
        return findings_provider_factory([])(name)

    code = run_cli(
        ["review", "--freeze", str(artifact.relative_to(tmp_path))],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        review_provider_factory=_tracking_factory,
    )
    assert code == 2
    assert provider_calls == []

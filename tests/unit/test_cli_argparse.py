"""Unit tests for CLI argument parsing."""

from __future__ import annotations

import pytest

from cli.main import build_parser, main
from cli.context import CliContext
from cli.output import OutputContext


def test_help_exits_zero() -> None:
    assert main(["--help"]) == 0


def test_version_exits_zero(capsys) -> None:
    code = main(["--version"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == "0.1.0"


def test_unknown_command_exits_one() -> None:
    assert main(["nope"]) == 1


def test_unknown_flag_exits_one() -> None:
    assert main(["status", "--not-a-flag"]) == 1


def test_init_global_options_parsed() -> None:
    from cli.args import extract_global_args

    parser = build_parser()
    raw = [
        "init",
        "-C",
        ".",
        "--config",
        "cfg.yaml",
        "--json",
        "-q",
        "-v",
        "--no-color",
        "--dry-run",
        "--force",
        "--non-interactive",
        "--regime",
        "git-only",
        "--repo-name",
        "x",
        "--docs-dir",
        "docs",
    ]
    global_argv, rest_argv = extract_global_args(raw)
    args = parser.parse_args(global_argv + rest_argv)
    assert args.command == "init"
    assert args.repo == "."
    assert args.json is True
    assert args.dry_run is True
    assert args.regime == "git-only"


def test_sync_options_parsed() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["sync", "--only", ".overseer/policy/*", "--only", "docs/*", "--force", "-y", "--dry-run"]
    )
    assert args.only == [".overseer/policy/*", "docs/*"]
    assert args.yes is True


def test_migrate_and_include_preserved_flags_parsed() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["init", "--migrate", "--include-preserved", "--force", "--non-interactive"]
    )
    assert args.migrate is True
    assert args.include_preserved is True
    assert args.force is True
    sync_args = parser.parse_args(["sync", "--include-preserved", "--force", "-y"])
    assert sync_args.include_preserved is True


def test_governance_sync_argparse() -> None:
    parser = build_parser()
    args = parser.parse_args(["governance-sync"])
    assert args.command == "governance-sync"
    assert args.write is False
    args_write = parser.parse_args(["governance-sync", "--write"])
    assert args_write.write is True


def test_workspace_argparse() -> None:
    parser = build_parser()
    status = parser.parse_args(["workspace", "status", "--strict-all"])
    assert status.command == "workspace"
    assert status.workspace_action == "status"
    assert status.strict_all is True
    check = parser.parse_args(["workspace", "check-next", "--lane", "security"])
    assert check.workspace_action == "check-next"
    assert check.lane == "security"
    doctor = parser.parse_args(["workspace", "doctor"])
    assert doctor.workspace_action == "doctor"
    composed = parser.parse_args(["status", "--workspace", "--exit-code"])
    assert composed.workspace is True
    assert composed.exit_code is True


def test_verify_step_argparse() -> None:
    from cli.args import extract_global_args

    parser = build_parser()
    raw = ["verify-step", "--step", "alpha", "--dry-run", "--json"]
    global_argv, rest_argv = extract_global_args(raw)
    args = parser.parse_args(global_argv + rest_argv)
    assert args.command == "verify-step"
    assert args.step == "alpha"
    assert args.dry_run is True
    assert args.json is True
    through_args = parser.parse_args(["verify-step", "--through", "current"])
    assert through_args.through == "current"


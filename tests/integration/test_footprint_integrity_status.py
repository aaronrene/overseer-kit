"""Integration: `overseer status` wires the footprint self-integrity gate (§KH3.5)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.support import FIXTURES, git_status_runner, run_cli


def _init(tmp_path: Path, runner, config_name: str = "config-git-only.yaml") -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / config_name), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )


def test_status_exit_code_2_when_self_footprint_file_missing(tmp_path: Path) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    # A real `init` renders every kit-owned destination for real; delete one to
    # reproduce the exact incident this gate exists to catch.
    (tmp_path / ".cursor" / "rules" / "governance-sync.mdc").unlink()
    code = run_cli(["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True)
    assert code == 2


def test_status_exit_code_0_when_self_footprint_complete(tmp_path: Path) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    code = run_cli(["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True)
    assert code == 0


def test_status_json_payload_reports_missing_self_footprint(tmp_path: Path, capsys) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    (tmp_path / ".cursor" / "rules" / "governance-sync.mdc").unlink()
    capsys.readouterr()  # discard `init` output before capturing the status payload
    run_cli(["status", "--json"], cwd=tmp_path, runner=runner, json_mode=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["footprint_self_integrity"]["state"] == "missing"
    assert payload["footprint_self_integrity"]["ok"] is False
    assert ".cursor/rules/governance-sync.mdc" in payload["footprint_self_integrity"]["missing"]
    assert payload["footprint_self_integrity"]["remediation"] == "ok sync"


def test_status_json_payload_reports_ok_when_complete(tmp_path: Path, capsys) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    capsys.readouterr()
    run_cli(["status", "--json"], cwd=tmp_path, runner=runner, json_mode=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["footprint_self_integrity"]["state"] == "ok"
    assert payload["footprint_self_integrity"]["ok"] is True


def test_existing_opt_in_content_digest_check_unchanged(tmp_path: Path, capsys) -> None:
    """Regression guard (§KH3.1 non-goal): --check-footprint content-digest behavior is untouched."""
    runner = git_status_runner()
    _init(tmp_path, runner)
    capsys.readouterr()
    code = run_cli(
        ["status", "--json", "--check-footprint", "--exit-code"],
        cwd=tmp_path,
        runner=runner,
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["footprint_integrity"] == "ok"

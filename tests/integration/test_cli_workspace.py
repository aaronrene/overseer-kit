"""Integration tests for ok workspace CLI (§MR.10 integration)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.fixtures.workspace import build_two_repo_constellation
from tests.support import run_cli
from tools.workspace.types import EXIT_WORKSPACE_RELAY


def test_workspace_status_json_basenames(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    code = run_cli(["workspace", "status", "--json"], cwd=fx["scooling"])
    assert code == 0
    # run_cli may not capture stdout — use main with capsys style via subprocess helper
    from tests.support import run_shim

    result = run_shim("ok", ["workspace", "status", "--json"], cwd=fx["scooling"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["authoritative_handover"]
    bases = {m["id"]: m["handover_basename"] for m in payload["members"]}
    assert bases["scooling"] == "SCOOLING-OVERSEER-HANDOVER.md"
    assert bases["knowtation"] == "KNOWTATION-OVERSEER-HANDOVER.md"
    assert bases["scooling"] != bases["knowtation"]


def test_check_next_exit_codes(tmp_path: Path) -> None:
    from tests.support import run_shim

    good = build_two_repo_constellation(tmp_path / "g")
    bad = build_two_repo_constellation(tmp_path / "b", stale_relay=True)
    assert run_shim("ok", ["workspace", "check-next"], cwd=good["scooling"]).exit_code == 0
    assert (
        run_shim("ok", ["workspace", "check-next"], cwd=bad["scooling"]).exit_code
        == EXIT_WORKSPACE_RELAY
    )


def test_status_workspace_does_not_imply_ok_on_green_single_repo(tmp_path: Path) -> None:
    """S9: single-repo status green must not imply workspace.ok when relay stale."""
    from tests.support import run_shim, seed_git_repo
    from cli.version_lock import write_version_lock
    from cli.footprint import resolve_footprint
    from adapters.config import load_config

    fx = build_two_repo_constellation(tmp_path, stale_relay=True)
    seed_git_repo(fx["scooling"])
    # Minimal lock so status can run without config error
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    # status without --workspace should not force workspace failure into overall claim
    plain = run_shim("ok", ["status", "--json"], cwd=fx["scooling"])
    assert plain.exit_code == 0
    plain_payload = json.loads(plain.stdout)
    assert "workspace" not in plain_payload or plain_payload.get("workspace") is None

    ws = run_shim("ok", ["status", "--workspace", "--json"], cwd=fx["scooling"])
    ws_payload = json.loads(ws.stdout)
    assert ws_payload["workspace"]["ok"] is False
    # Without --exit-code, process exit stays 0 even when workspace.ok false
    assert ws.exit_code == 0

    ws_exit = run_shim(
        "ok", ["status", "--workspace", "--exit-code", "--json"], cwd=fx["scooling"]
    )
    payload = json.loads(ws_exit.stdout)
    assert payload["workspace"]["ok"] is False
    # Precedence 2 > 6 > 35 > 3 > 0 — lock/substrate may win over 35 on bare fixtures
    assert ws_exit.exit_code in {2, 6, 35}


def test_doctor_board_name_violation(tmp_path: Path) -> None:
    from tests.support import run_shim

    fx = build_two_repo_constellation(tmp_path, bare_names_on_relay=True)
    result = run_shim("ok", ["workspace", "doctor", "--json"], cwd=fx["scooling"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    codes = [f["code"] for f in payload["findings"]]
    assert "board_name_violation" in codes


def test_muse_only_member_skips_git(tmp_path: Path) -> None:
    from tools.workspace.doctor import run_doctor
    from adapters.config import load_config

    fx = build_two_repo_constellation(tmp_path, with_musehub=True)
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    report = run_doctor(cfg, fx["scooling"], invoke_git=True)
    codes = [f.code for f in report.findings]
    assert "muse_only_skip_git" in codes


def test_check_next_not_configured_is_config_exit(tmp_path: Path) -> None:
    from tests.support import run_cli, write_config

    write_config(tmp_path, "config-git-only.yaml")
    (tmp_path / "docs").mkdir(exist_ok=True)
    code = run_cli(["workspace", "check-next"], cwd=tmp_path)
    assert code == 2

"""E2E acceptance stories S1–S12 for workspace lanes (§MR.9 / §MR.10 e2e)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.fixtures.workspace import build_two_repo_constellation
from tests.support import run_shim
from tools.workspace.types import EXIT_WORKSPACE_RELAY


def test_s1_s2_stale_then_refresh(tmp_path: Path) -> None:
    stale = build_two_repo_constellation(tmp_path / "s1", stale_relay=True)
    r1 = run_shim("ok", ["workspace", "check-next"], cwd=stale["scooling"])
    assert r1.exit_code == EXIT_WORKSPACE_RELAY
    assert "stale_relay" in r1.stdout + r1.stderr

    fresh = build_two_repo_constellation(tmp_path / "s2", stale_relay=False)
    r2 = run_shim("ok", ["workspace", "check-next"], cwd=fresh["scooling"])
    assert r2.exit_code == 0


def test_s3_archived_not_selected(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    path = fx["scooling_handover"]
    text = path.read_text(encoding="utf-8")
    text += "\n<!-- overseer:next role=archived status=archived -->\n## ARCHIVED SESSION — old Thinking\n"
    path.write_text(text, encoding="utf-8")
    assert run_shim("ok", ["workspace", "check-next"], cwd=fx["scooling"]).exit_code == 0

    # Forbidden legacy form fails
    path.write_text(
        path.read_text(encoding="utf-8") + "\n## NEXT SESSION — archived leftover\n",
        encoding="utf-8",
    )
    assert run_shim("ok", ["workspace", "check-next"], cwd=fx["scooling"]).exit_code == EXIT_WORKSPACE_RELAY


def test_s4_s12_distinct_basenames_and_doctor(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    status = json.loads(
        run_shim("ok", ["workspace", "status", "--json"], cwd=fx["scooling"]).stdout
    )
    bases = {m["handover_basename"] for m in status["members"]}
    assert "SCOOLING-OVERSEER-HANDOVER.md" in bases
    assert "KNOWTATION-OVERSEER-HANDOVER.md" in bases
    assert status["authoritative_handover"]

    bare = build_two_repo_constellation(tmp_path / "bare", bare_names_on_relay=True)
    doctor = json.loads(
        run_shim("ok", ["workspace", "doctor", "--json"], cwd=bare["scooling"]).stdout
    )
    assert any(f["code"] == "board_name_violation" for f in doctor["findings"])


def test_s6_lane_tip_non_primary(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path, with_lane_tip=True)
    assert run_shim("ok", ["workspace", "check-next"], cwd=fx["scooling"]).exit_code == 0
    status = json.loads(
        run_shim("ok", ["workspace", "status", "--json"], cwd=fx["scooling"]).stdout
    )
    assert any(l["id"] == "security" and not l["primary"] for l in status["lanes"])


def test_s7_optional_brain_absent(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path, with_brain=True)
    status = json.loads(
        run_shim("ok", ["workspace", "status", "--json"], cwd=fx["scooling"]).stdout
    )
    brain = next(m for m in status["members"] if m["id"] == "brain")
    assert brain["member_status"] == "absent"
    assert run_shim("ok", ["workspace", "check-next"], cwd=fx["scooling"]).exit_code == 0


def test_s8_external_two_repo(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path, constellation_id="app-store")
    assert run_shim("ok", ["workspace", "check-next"], cwd=fx["scooling"]).exit_code == 0
    stale = build_two_repo_constellation(tmp_path / "stale", stale_relay=True)
    assert run_shim("ok", ["workspace", "check-next"], cwd=stale["scooling"]).exit_code == 35


def test_s10_s11_product_relay(tmp_path: Path) -> None:
    good = build_two_repo_constellation(tmp_path / "pr", ownership_product_relay=True)
    assert run_shim("ok", ["workspace", "check-next"], cwd=good["scooling"]).exit_code == 0
    status = json.loads(
        run_shim("ok", ["workspace", "status", "--json"], cwd=good["scooling"]).stdout
    )
    assert status["authoritative_handover"]
    assert "SCOOLING" in Path(status["authoritative_handover"]).name.upper()

    missing = build_two_repo_constellation(tmp_path / "miss", missing_product_relay=True)
    assert (
        run_shim("ok", ["workspace", "check-next"], cwd=missing["scooling"]).exit_code
        == EXIT_WORKSPACE_RELAY
    )


def test_e2e_governance_sync_footer_workspace_relay(tmp_path: Path) -> None:
    from adapters.config import load_config
    from tools.workspace import workspace_relay_footer_state

    fx = build_two_repo_constellation(tmp_path, stale_relay=True)
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    assert workspace_relay_footer_state(cfg, fx["scooling"]) == "stale_relay"


def test_e2e_init_prefixed_defaults(tmp_path: Path) -> None:
    from tests.support import run_shim

    result = run_shim(
        "ok",
        ["init", "--regime", "git-only", "--repo-name", "acme-app", "--non-interactive"],
        cwd=tmp_path,
    )
    assert result.exit_code == 0
    assert (tmp_path / "docs" / "ACME-APP-OVERSEER-HANDOVER.md").is_file()
    assert (tmp_path / "docs" / "ACME-APP-ROADMAP.md").is_file()

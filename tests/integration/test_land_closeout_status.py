"""Integration: land-closeout wiring across status / land-closeout / land-check /
governance-sync (§PMHF.10 integration)."""

from __future__ import annotations

import io
import json
import subprocess
from contextlib import redirect_stdout
from pathlib import Path

from adapters.config import load_config
from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    git_status_runner,
    land_a_fence_body,
    land_handover_text,
    land_roadmap_text,
    make_runner,
    ok,
    run_cli,
    seed_land_repo,
)
from tools.close_ritual.land_check import run_land_check


def _seed_via_init(tmp_path: Path, *, claim: str, marker_tip: str | None) -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=git_status_runner(tip="cafebabe"),
        )
        == 0
    )
    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text(
        land_handover_text(claim), encoding="utf-8"
    )
    (tmp_path / "docs" / "ROADMAP.md").write_text(land_roadmap_text(), encoding="utf-8")
    marker = tmp_path / ".overseer" / "last_governance_sync"
    if marker_tip is None:
        if marker.exists():
            marker.unlink()
    else:
        marker.write_text(
            f"2026-07-30T00:00:00Z\nr1={marker_tip}\nr3={marker_tip}\n", encoding="utf-8"
        )


def test_status_exit_2_post_merge_incomplete_when_land_a_and_d1_drifted(
    tmp_path: Path, capsys
) -> None:
    _seed_via_init(tmp_path, claim="deadbeef", marker_tip="cafebabe")
    capsys.readouterr()
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=git_status_runner(tip="cafebabe"),
        json_mode=True,
    )
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["land_closeout"]["state"] == "post_merge_incomplete"
    assert payload["land_closeout"]["ok"] is False
    assert payload["land_closeout"]["land_phase"] == "land-a"
    assert payload["land_closeout"]["remediation"].startswith("land-b required:")


def test_status_exit_0_when_land_a_and_aligned(tmp_path: Path, capsys) -> None:
    _seed_via_init(tmp_path, claim="cafebabe", marker_tip="cafebabe")
    capsys.readouterr()
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=git_status_runner(tip="cafebabe"),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["land_closeout"]["state"] == "land_a_in_progress"
    assert payload["land_closeout"]["ok"] is True


def test_land_closeout_command_exit_codes(tmp_path: Path, capsys) -> None:
    _seed_via_init(tmp_path, claim="cafebabe", marker_tip="cafebabe")
    capsys.readouterr()
    code = run_cli(
        ["land-closeout", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(tip="cafebabe"),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["state"] == "land_a_in_progress"
    assert payload["exit_code"] == 0

    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text(
        land_handover_text("deadbeef"), encoding="utf-8"
    )
    capsys.readouterr()
    code = run_cli(
        ["land-closeout", "--json"],
        cwd=tmp_path,
        runner=git_status_runner(tip="cafebabe"),
        json_mode=True,
    )
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["state"] == "post_merge_incomplete"
    assert payload["exit_code"] == 2


def test_land_closeout_human_output_frozen_tokens(tmp_path: Path, capsys) -> None:
    _seed_via_init(tmp_path, claim="deadbeef", marker_tip="cafebabe")
    capsys.readouterr()
    code = run_cli(
        ["land-closeout"],
        cwd=tmp_path,
        runner=git_status_runner(tip="cafebabe"),
    )
    out = capsys.readouterr().out
    assert code == 2
    assert "land_closeout: post_merge_incomplete" in out
    assert (
        "land_closeout-remediation: land-b required: ok governance-sync --dry-run "
        "then apply; paste land-b; do not re-paste land-a"
    ) in out


# --- ok land-check refusal (§PMHF.6.2) ---


def _ritual_config_yaml(tmp_path: Path) -> Path:
    cfg = tmp_path / ".overseer" / "config.yaml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(
        """
overseer_config_version: 1
repo:
  name: fixture
  root_relative_docs: "docs"
vcs:
  regime: git-only
  canonical: git
  git:
    remote: origin
    main_branch: main
    mirror_branch: null
    feature_branch_pattern: "feat/{slug}"
  muse:
    staging_remote: null
    main_branch: null
    working_dir: null
docs:
  handover: OVERSEER-HANDOVER.md
  roadmap: ROADMAP.md
  standing_decisions: ROADMAP.md
thresholds:
  realign_max_commits: 50
  drift_warn_only: true
freeze_contract:
  enabled: true
  reviewer:
    mode: agent
    model: thinking-high
    provider: local
    fallback: human
  human_escalation: [security]
close_ritual:
  enabled: true
  mode: verify_landed
  require_paths: ["BOARD.json"]
""",
        encoding="utf-8",
    )
    return cfg


def _seed_land_check_repo(tmp_path: Path, *, handover_text: str) -> object:
    init = subprocess.run(
        ["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True, text=True
    )
    assert init.returncode == 0, init.stderr
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True
    )
    (tmp_path / "BOARD.json").write_text('{"ok": true}\n', encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True
    )
    cfg_path = _ritual_config_yaml(tmp_path)
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        'installed_at: "2026-01-01T00:00:00Z"\nsynced_at: "2026-01-01T00:00:00Z"\n'
        "footprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(handover_text, encoding="utf-8")
    (docs / "ROADMAP.md").write_text(land_roadmap_text(), encoding="utf-8")
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        "2026-07-30T00:00:00Z\nr1=cafebabe\nr3=cafebabe\n", encoding="utf-8"
    )
    return load_config(cfg_path)


def test_land_check_refuses_landed_while_land_a(tmp_path: Path) -> None:
    config = _seed_land_check_repo(tmp_path, handover_text=land_handover_text("cafebabe"))
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
        }
    )
    result = run_land_check(config, tmp_path, runner=runner)
    assert result.exit_code == 2
    assert result.landed is False
    assert any("land_closeout: land_a_in_progress" in m for m in result.messages)


def test_land_check_refuses_landed_on_post_merge_incomplete(tmp_path: Path) -> None:
    handover = land_handover_text(
        "cafebabe",
        fence_body=land_a_fence_body(paste_extra="PR #206 open — waiting for merge.\n"),
    )
    config = _seed_land_check_repo(tmp_path, handover_text=handover)
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr view 206 --json state,mergedAt": ok(
                '{"state": "MERGED", "mergedAt": "2026-07-30T12:00:00Z"}'
            ),
        }
    )
    result = run_land_check(config, tmp_path, runner=runner)
    assert result.exit_code == 2
    assert result.landed is False
    assert any("land_closeout: post_merge_incomplete" in m for m in result.messages)
    assert any("land-b required:" in m for m in result.messages)
    assert not any("landed: true" in m.lower() for m in result.messages)


# --- governance-sync dry-run plans land-b (§PMHF.3.4) ---


def _sync_runner():
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                "[]"
            ),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )


def test_governance_sync_dry_run_plans_land_b_when_land_a_and_drifted(
    tmp_path: Path,
) -> None:
    seed_land_repo(tmp_path, claim="deadbeef")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    before_h = handover.read_text(encoding="utf-8")

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync"],
            cwd=tmp_path,
            runner=_sync_runner(),
            kit=kit_root(),
        )
    out = buf.getvalue()
    assert code == 0
    assert "next_regen: regenerated (land-b)" in out
    # §PMHF.3.4 rule 4: dry-run shows the planned land-b body; no doc writes.
    assert "land-phase: land-b" in out
    assert "ID: PMHF land-b (post-merge sync)" in out
    assert handover.read_text(encoding="utf-8") == before_h


def test_governance_sync_preserves_land_a_paste_mid_wait(tmp_path: Path) -> None:
    # Land-a posture + D3-only drift must not clobber the land-a paste (fail closed).
    seed_land_repo(
        tmp_path,
        claim="cafebabe",
        roadmap_text=land_roadmap_text(
            "| **PMHF → main** | Operator + Auto | **TODO** | Land PMHF |",
        ),
    )
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                '[{"number": 999, "title": "PMHF land hygiene", '
                '"mergeCommit": {"oid": "abcabcabc"}, "mergedAt": "2026-07-30T00:00:00Z"}]'
            ),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    out = buf.getvalue()
    assert code == 0
    assert "next_regen: human_authorship_required (land_a_in_progress)" in out

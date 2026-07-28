"""Integration: status --exit-code + dry-run marker stamp (§GFG.9 integration)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    git_status_runner,
    make_runner,
    ok,
    run_cli,
    seed_governance_freshness,
    write_config,
)


def _aligned_handover(tip: str = "cafebabe") -> str:
    return (
        f"| GitHub `main` | `{tip}` |\n"
        f"| **main HEAD** | `{tip}` |\n"
    )


def _seed_aligned(tmp_path: Path, tip: str = "cafebabe") -> None:
    write_config(tmp_path, "config-git-only.yaml")
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        "installed_at: \"2026-01-01T00:00:00Z\"\nsynced_at: \"2026-01-01T00:00:00Z\"\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(_aligned_handover(tip), encoding="utf-8")
    (docs / "ROADMAP.md").write_text("## Build queue\n\n", encoding="utf-8")


def _runner(tip: str = "cafebabe"):
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok(tip),
            "gh pr list": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )


def test_status_exit_2_when_d1_drifted(tmp_path: Path, capsys) -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=git_status_runner(tip="cafebabe"),
        )
        == 0
    )
    handover = tmp_path / "docs"
    # Prefer whatever init wrote; force stale claim
    for path in handover.glob("*HANDOVER*"):
        path.write_text("| GitHub `main` | `deadbeef` |\n", encoding="utf-8")
    capsys.readouterr()
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=git_status_runner(tip="cafebabe"),
        json_mode=True,
    )
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["governance_freshness"]["state"] == "drifted"


def test_status_exit_2_when_marker_absent(tmp_path: Path, capsys) -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=git_status_runner(),
        )
        == 0
    )
    tip = "cafebabe"
    for path in (tmp_path / "docs").glob("*HANDOVER*"):
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.rstrip() + f"\n\n| Item | Value |\n| --- | --- |\n| GitHub `main` | `{tip}` |\n",
            encoding="utf-8",
        )
    marker = tmp_path / ".overseer" / "last_governance_sync"
    if marker.exists():
        marker.unlink()
    capsys.readouterr()
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=git_status_runner(tip=tip),
        json_mode=True,
    )
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["governance_freshness"]["state"] == "stale_marker"


def test_status_exit_0_when_aligned_and_marker_matches(tmp_path: Path, capsys) -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=git_status_runner(),
        )
        == 0
    )
    seed_governance_freshness(tmp_path)
    capsys.readouterr()
    code = run_cli(
        ["status", "--json", "--exit-code"],
        cwd=tmp_path,
        runner=git_status_runner(),
        json_mode=True,
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["governance_freshness"]["state"] == "ok"
    assert payload["governance_freshness"]["ok"] is True
    # timestamp-only legacy surface
    assert payload["last_governance_sync"]
    assert "\n" not in payload["last_governance_sync"]


def test_dry_run_aligned_stamps_marker_without_doc_writes(tmp_path: Path) -> None:
    _seed_aligned(tmp_path)
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    roadmap = tmp_path / "docs" / "ROADMAP.md"
    before_h = handover.read_text(encoding="utf-8")
    before_r = roadmap.read_text(encoding="utf-8")
    runner = _runner()
    code = run_cli(
        ["governance-sync", "--json"],
        cwd=tmp_path,
        runner=runner,
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    assert handover.read_text(encoding="utf-8") == before_h
    assert roadmap.read_text(encoding="utf-8") == before_r
    marker = tmp_path / ".overseer" / "last_governance_sync"
    assert marker.is_file()
    body = marker.read_text(encoding="utf-8")
    assert "r1=cafebabe" in body
    assert "r3=cafebabe" in body

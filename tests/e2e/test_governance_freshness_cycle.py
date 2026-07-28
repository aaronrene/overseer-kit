"""E2E freshness cycle + land-check gate (§GFG.9 e2e)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
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
from tools.close_ritual.land_check import run_land_check


def test_stale_to_fresh_status_cycle(tmp_path: Path) -> None:
    tip = "cafebabe"
    runner = git_status_runner(tip=tip)
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    for path in (tmp_path / "docs").glob("*HANDOVER*"):
        path.write_text("| GitHub `main` | `deadbeef` |\n", encoding="utf-8")

    assert (
        run_cli(
            ["status", "--exit-code"],
            cwd=tmp_path,
            runner=git_status_runner(tip=tip),
        )
        == 2
    )

    # Align docs + stamp via dry-run when D1/D2 aligned
    for path in (tmp_path / "docs").glob("*HANDOVER*"):
        path.write_text(f"| GitHub `main` | `{tip}` |\n", encoding="utf-8")
    sync_runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok(tip),
            "gh pr list": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    assert (
        run_cli(
            ["governance-sync"],
            cwd=tmp_path,
            runner=sync_runner,
            kit=kit_root(),
        )
        == 0
    )
    assert (tmp_path / ".overseer" / "last_governance_sync").is_file()
    assert (
        run_cli(
            ["status", "--exit-code"],
            cwd=tmp_path,
            runner=git_status_runner(tip=tip),
        )
        == 0
    )


def test_land_check_fails_on_freshness_when_enabled(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    cfg_path = tmp_path / ".overseer" / "config.yaml"
    text = cfg_path.read_text(encoding="utf-8")
    text += (
        "\nclose_ritual:\n"
        "  enabled: true\n"
        "  mode: verify_landed\n"
        "  require_paths:\n"
        "    - docs/OVERSEER-HANDOVER.md\n"
    )
    cfg_path.write_text(text, encoding="utf-8")
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        "installed_at: \"2026-01-01T00:00:00Z\"\nsynced_at: \"2026-01-01T00:00:00Z\"\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    handover = docs / "OVERSEER-HANDOVER.md"
    handover.write_text("| GitHub `main` | `deadbeef` |\n", encoding="utf-8")

    # Make require_paths "match" main by using a fake git repo without remote —
    # land-check will fail path match first OR freshness. Seed a matching main
    # is hard without git; instead use prepare_pr with clean paths after making
    # a real git repo and committing the file, then still fail on freshness.
    import subprocess

    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "t"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "docs/OVERSEER-HANDOVER.md"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    config = load_config(cfg_path)
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
        }
    )
    result = run_land_check(config, tmp_path, runner=runner)
    assert result.exit_code == 2
    assert any("governance_freshness" in m for m in result.messages)

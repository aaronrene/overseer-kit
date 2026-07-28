"""Data-integrity: dry-run marker stamp rules (§GFG.9 data-integrity)."""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import make_runner, ok, run_cli, write_config


def _seed(tmp_path: Path, *, claim: str) -> None:
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
    (docs / "OVERSEER-HANDOVER.md").write_text(
        f"| GitHub `main` | `{claim}` |\n", encoding="utf-8"
    )
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


def test_dry_run_aligned_writes_marker_docs_unchanged(tmp_path: Path) -> None:
    _seed(tmp_path, claim="cafebabe")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    roadmap = tmp_path / "docs" / "ROADMAP.md"
    before_h = handover.read_bytes()
    before_r = roadmap.read_bytes()
    code = run_cli(
        ["governance-sync"],
        cwd=tmp_path,
        runner=_runner(),
        kit=kit_root(),
    )
    assert code == 0
    assert handover.read_bytes() == before_h
    assert roadmap.read_bytes() == before_r
    marker = tmp_path / ".overseer" / "last_governance_sync"
    assert marker.is_file()
    assert b"r1=cafebabe" in marker.read_bytes()


def test_dry_run_d1_drifted_no_marker(tmp_path: Path) -> None:
    _seed(tmp_path, claim="deadbeef")
    code = run_cli(
        ["governance-sync"],
        cwd=tmp_path,
        runner=_runner(),
        kit=kit_root(),
    )
    assert code == 0
    assert not (tmp_path / ".overseer" / "last_governance_sync").exists()
    assert (tmp_path / "docs" / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8").count(
        "deadbeef"
    ) == 1


def test_idempotent_double_dry_run_aligned(tmp_path: Path) -> None:
    _seed(tmp_path, claim="cafebabe")
    runner = _runner()
    assert run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root()) == 0
    first = (tmp_path / ".overseer" / "last_governance_sync").read_text(encoding="utf-8")
    assert run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root()) == 0
    second = (tmp_path / ".overseer" / "last_governance_sync").read_text(encoding="utf-8")
    assert "r1=cafebabe" in first
    assert "r1=cafebabe" in second

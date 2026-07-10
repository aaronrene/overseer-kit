"""Stress tests for large footprint handling."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import read_version_lock
from tests.support import run_cli


def test_large_footprint_only_scope(tmp_path: Path, monkeypatch) -> None:
    kit = tmp_path / "kit"
    kit.mkdir()
    (kit / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    for sub in ("templates", "policy", "cursor/rules", "cursor/skills/big"):
        (kit / sub).mkdir(parents=True)
    (kit / "templates" / "OVERSEER-HANDOVER.template.md").write_text("# {{repo.name}}\n", encoding="utf-8")
    (kit / "templates" / "ROADMAP.template.md").write_text("# Roadmap\n", encoding="utf-8")
    (kit / "templates" / "STANDING-DECISIONS.template.md").write_text("| SD-1 |\n", encoding="utf-8")

    for index in range(200):
        (kit / "policy" / f"p{index}.yaml").write_text(f"k: {index}\n", encoding="utf-8")
        (kit / "cursor" / "rules" / f"r{index}.mdc").write_text(f"rule {index}\n", encoding="utf-8")
    (kit / "cursor" / "skills" / "big" / "SKILL.md").write_text("x" * 100_000 + "\n", encoding="utf-8")

    repo = tmp_path / "repo"
    repo.mkdir()
    assert run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=repo,
        kit=kit,
    ) == 0

    conflict = repo / ".overseer" / "policy" / "p0.yaml"
    conflict.write_text("edited\n", encoding="utf-8")

    code = run_cli(
        ["sync", "-y", "--only", ".overseer/policy/p1.yaml"],
        cwd=repo,
        kit=kit,
    )
    assert code == 0
    lock = read_version_lock(repo / ".overseer" / "version.lock")
    assert len(lock.footprint) >= 200

"""Data integrity — ``ok next`` is read-only and idempotent (§ONS.12)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, write_config


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_twice_identical_no_mutation(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    handover = docs / "OVERSEER-HANDOVER.md"
    roadmap = docs / "ROADMAP.md"
    handover.write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    roadmap.write_text("# Roadmap\n", encoding="utf-8")
    lock = tmp_path / ".overseer" / "version.lock"
    lock.write_text("kit_version: 0.1.0\n", encoding="utf-8")

    before = {
        "handover": _sha(handover),
        "roadmap": _sha(roadmap),
        "lock": _sha(lock),
    }
    runner = git_status_runner()
    code1 = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    out1 = capsys.readouterr().out
    code2 = run_cli(["next"], cwd=tmp_path, runner=runner, kit=kit_root())
    out2 = capsys.readouterr().out
    assert code1 == 0
    assert code2 == 0
    assert out1 == out2
    assert _sha(handover) == before["handover"]
    assert _sha(roadmap) == before["roadmap"]
    assert _sha(lock) == before["lock"]

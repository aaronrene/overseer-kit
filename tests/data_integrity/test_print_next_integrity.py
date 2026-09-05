"""Data integrity — ``ok next`` is read-only and idempotent (§ONS.12 / §NXP.8)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, write_config
from tools.print_next.extract import CURRENT_NEXT_HEADING, set_read_at_clock
from tools.governance_hygiene.next_regen import extract_paste_fence_body

FIXED_READ_AT = "2026-09-04T12:00:00Z"


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
    set_read_at_clock(lambda: FIXED_READ_AT)
    try:
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
    finally:
        set_read_at_clock(None)


def test_fence_body_and_heading_byte_identical_to_pre_nxp(tmp_path: Path, capsys) -> None:
    """§NXP.8 data-integrity: fence body + CURRENT_NEXT_HEADING unchanged."""
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    text = (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8")
    handover = docs / "OVERSEER-HANDOVER.md"
    handover.write_text(text, encoding="utf-8")
    (docs / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")

    pre_body = extract_paste_fence_body(text)
    assert pre_body is not None
    assert CURRENT_NEXT_HEADING == "## CURRENT NEXT — paste this"

    set_read_at_clock(lambda: FIXED_READ_AT)
    try:
        code = run_cli(["next"], cwd=tmp_path, runner=git_status_runner(), kit=kit_root())
        out = capsys.readouterr().out
        assert code == 0
        assert out.startswith(CURRENT_NEXT_HEADING + "\n\n")
        # Fence body between ```text and closing ``` must match pre-NXP extract.
        start = out.index("```text\n") + len("```text\n")
        end = out.rindex("\n```\n")
        emitted_body = out[start:end]
        if not emitted_body.endswith("\n"):
            # format always ensures trailing newline on body before closing fence
            pass
        # format_current_next ensures body ends with newline; extract may or may not.
        expected = pre_body if pre_body.endswith("\n") else pre_body + "\n"
        assert emitted_body == expected.rstrip("\n") or emitted_body == expected.rstrip("\n") + "\n"
        # Stronger: body content without trailing newline equality
        assert emitted_body.rstrip("\n") == pre_body.rstrip("\n")
    finally:
        set_read_at_clock(None)

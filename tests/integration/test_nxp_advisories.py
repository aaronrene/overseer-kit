"""Integration — NXP check-next + status board-name advisories (§NXP.5 / §NXP.6)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, run_cli, write_config
from tools.workspace.board_names import (
    check_next_unconfigured_advisory,
    expected_handover_basename,
    status_board_name_advisory,
)


def test_check_next_unconfigured_bare_advisory(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "OVERSEER-HANDOVER.md").write_text("# h\n", encoding="utf-8")
    (tmp_path / "docs" / "ROADMAP.md").write_text("# r\n", encoding="utf-8")
    code = run_cli(["workspace", "check-next"], cwd=tmp_path, kit=kit_root())
    out = capsys.readouterr().out
    assert code == 0
    assert "workspace not configured" in out
    assert "OVERSEER-HANDOVER.md" in out
    assert "TEST-GIT-OVERSEER-HANDOVER.md" in out


def test_check_next_unconfigured_compliant_advisory(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    cfg_path = tmp_path / ".overseer" / "config.yaml"
    text = cfg_path.read_text(encoding="utf-8")
    text = text.replace(
        "handover: OVERSEER-HANDOVER.md",
        "handover: TEST-GIT-OVERSEER-HANDOVER.md",
    ).replace("roadmap: ROADMAP.md", "roadmap: TEST-GIT-ROADMAP.md")
    cfg_path.write_text(text, encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "TEST-GIT-OVERSEER-HANDOVER.md").write_text("# h\n", encoding="utf-8")
    (docs / "TEST-GIT-ROADMAP.md").write_text("# r\n", encoding="utf-8")
    code = run_cli(["workspace", "check-next"], cwd=tmp_path, kit=kit_root())
    out = capsys.readouterr().out
    assert code == 0
    assert "board names already compliant" in out


def test_status_advisory_when_bare(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    # Minimal lock so status proceeds past lock_error into advisory path.
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: "
        + ("0" * 64)
        + "\ninstalled_at: 2026-01-01T00:00:00Z\nsynced_at: 2026-01-01T00:00:00Z\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    code = run_cli(
        ["status"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "board naming:" in out
    assert "OVERSEER-HANDOVER.md" in out or "prefer" in out


def test_status_advisory_absent_when_prefixed(tmp_path: Path, capsys) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    cfg_path = tmp_path / ".overseer" / "config.yaml"
    text = cfg_path.read_text(encoding="utf-8")
    text = text.replace(
        "handover: OVERSEER-HANDOVER.md",
        "handover: TEST-GIT-OVERSEER-HANDOVER.md",
    ).replace("roadmap: ROADMAP.md", "roadmap: TEST-GIT-ROADMAP.md")
    cfg_path.write_text(text, encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "TEST-GIT-OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "print-next-handover.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "TEST-GIT-ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: "
        + ("0" * 64)
        + "\ninstalled_at: 2026-01-01T00:00:00Z\nsynced_at: 2026-01-01T00:00:00Z\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    code = run_cli(
        ["status"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "board naming:" not in out


def test_advisory_helpers_unit(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    msg = check_next_unconfigured_advisory(config)
    assert "OVERSEER-HANDOVER.md" in msg
    assert expected_handover_basename("test-git") in msg
    status_msg = status_board_name_advisory(config)
    assert status_msg is not None
    assert "board naming:" in status_msg

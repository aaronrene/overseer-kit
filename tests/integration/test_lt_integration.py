"""Integration tests for LT loop tightening (§LT.10)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import yaml

from cli.footprint import resolve_footprint
from tests.support import FIXTURES, KIT_ROOT, git_status_runner, run_cli
from tools.governance_freshness import GovernanceFreshnessReport

_OK_FRESHNESS = GovernanceFreshnessReport(
    state="ok",
    message="patched",
    remediation=None,
    d1="aligned",
    d2="aligned",
    marker_present=True,
)


def _init(tmp_path: Path, runner, config_name: str = "config-git-only.yaml") -> None:
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / config_name), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )


def test_status_exit_2_when_coverage_missing_dest(tmp_path: Path) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    lock_path = tmp_path / ".overseer" / "version.lock"
    lock = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
    lock["footprint"] = lock["footprint"][:5]
    lock_path.write_text(yaml.dump(lock, sort_keys=False), encoding="utf-8")
    with patch("cli.commands.status.check_governance_freshness", return_value=_OK_FRESHNESS):
        code = run_cli(
            ["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True
        )
    assert code == 2


def test_status_not_2_from_coverage_after_lock_updated(tmp_path: Path) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    with patch("cli.commands.status.check_governance_freshness", return_value=_OK_FRESHNESS):
        code = run_cli(
            ["status", "--json", "--exit-code"], cwd=tmp_path, runner=runner, json_mode=True
        )
    assert code == 0


def test_session_bookends_in_resolve_when_enabled(tmp_path: Path) -> None:
    from adapters.config import load_config

    config = load_config(FIXTURES / "config-git-only.yaml")
    from dataclasses import replace

    off = replace(config, session_bookends=replace(config.session_bookends, enabled=False))
    on = replace(config, session_bookends=replace(config.session_bookends, enabled=True))
    off_dests = {f.destination for f in resolve_footprint(off, kit=KIT_ROOT)}
    on_dests = {f.destination for f in resolve_footprint(on, kit=KIT_ROOT)}
    hook_dests = {
        ".cursor/hooks.json",
        ".cursor/hooks/session-start-next.sh",
        ".cursor/hooks/session-end-closeout.sh",
        ".cursor/hooks/README.md",
    }
    assert hook_dests.isdisjoint(off_dests)
    assert hook_dests <= on_dests


def test_compact_write_creates_archive(tmp_path: Path) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    text = handover.read_text(encoding="utf-8")
    bullets = "\n\n".join(f"- **2026-01-{day:02d}** — entry {day}" for day in range(1, 21))
    if "<!-- overseer:anchor:change-log -->" in text:
        start = text.index("<!-- overseer:anchor:change-log -->")
        end = text.index("<!-- /overseer:anchor:change-log -->")
        text = (
            text[: start + len("<!-- overseer:anchor:change-log -->")]
            + "\n"
            + bullets
            + "\n"
            + text[end:]
        )
    else:
        text += (
            "\n<!-- overseer:anchor:change-log -->\n"
            + bullets
            + "\n<!-- /overseer:anchor:change-log -->\n"
        )
    handover.write_text(text, encoding="utf-8")
    code = run_cli(
        ["handover-compact", "--write", "--keep", "15"],
        cwd=tmp_path,
        runner=runner,
    )
    assert code == 0
    archive = tmp_path / "docs" / "archive" / "handover" / "CHANGE-LOG.md"
    assert archive.is_file()
    living = handover.read_text(encoding="utf-8")
    assert "Older entries: docs/archive/handover/CHANGE-LOG.md" in living
    assert living.count("- **2026-") <= 15


def test_handover_compact_both_flags_exit_2(tmp_path: Path) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    code = run_cli(
        ["handover-compact", "--write", "--dry-run"],
        cwd=tmp_path,
        runner=runner,
    )
    assert code == 2


def test_status_json_includes_footprint_coverage(tmp_path: Path, capsys) -> None:
    runner = git_status_runner()
    _init(tmp_path, runner)
    capsys.readouterr()
    with patch("cli.commands.status.check_governance_freshness", return_value=_OK_FRESHNESS):
        run_cli(["status", "--json"], cwd=tmp_path, runner=runner, json_mode=True)
    payload = json.loads(capsys.readouterr().out)
    assert "footprint_coverage" in payload
    assert "ide_workspace_hint" in payload
    assert "optional_feature_tips" in payload
    assert payload["optional_feature_tips"]["tips"]

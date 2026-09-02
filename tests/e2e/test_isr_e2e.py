"""E2e tests for ISR active-slice gate + Mode D CLI (§ISR.11)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from cli.kit_root import kit_root
from tests.fixtures.isr import load_isr_entry, seed_isr_repo
from tests.support import FIXTURES, git_status_runner, muse_mirror_status_runner, run_cli, seed_muse_substrate
from tools.governance_freshness import GovernanceFreshnessReport
from tools.honesty.genesis import build_genesis_entry
from tools.honesty.ledger_io import serialize_entry

_OK_FRESHNESS = GovernanceFreshnessReport(
    state="ok",
    message="patched",
    remediation=None,
    d1="aligned",
    d2="aligned",
    marker_present=True,
)


def _seed_status_repo(tmp_path: Path, *, require: str) -> None:
    runner = git_status_runner()
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    cfg = tmp_path / ".overseer" / "config.yaml"
    base = (FIXTURES / "config-git-only.yaml").read_text(encoding="utf-8")
    cfg.write_text(
        base
        + f"""
honesty:
  enabled: true
  ledger: .overseer/honesty/VERDICT-LEDGER.jsonl
  require_independent_second_reviewer: {require}
""",
        encoding="utf-8",
    )
    ledger_dir = tmp_path / ".overseer" / "honesty"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    genesis = serialize_entry(build_genesis_entry("2026-01-01T00:00:00Z"))
    (ledger_dir / "VERDICT-LEDGER.jsonl").write_text(genesis + "\n", encoding="utf-8")
    docs = tmp_path / "docs"
    (docs / "ROADMAP.md").write_text(
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        "| **ISR-b Independent second reviewer build** | Auto | **DONE** | "
        "`docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md` |\n",
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "## NEXT SESSION — ISR-b\n\n| | |\n| **ID** | **ISR-b** |\n\n"
        "Build verified → `pass` (ISR-b-BV-r1).\n",
        encoding="utf-8",
    )


def test_warn_mode_done_without_ledger_status_exit_0(tmp_path: Path, capsys) -> None:
    _seed_status_repo(tmp_path, require="warn")
    runner = git_status_runner()
    capsys.readouterr()
    with patch("cli.commands.status.check_governance_freshness", return_value=_OK_FRESHNESS):
        code = run_cli(
            ["status", "--json", "--exit-code"],
            cwd=tmp_path,
            runner=runner,
            json_mode=True,
        )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    gate = payload.get("independent_second_reviewer_gate")
    assert gate is not None
    assert gate["ok"] is True
    assert gate["mode"] == "warn"
    assert gate["matched"] is False


def test_require_mode_done_without_ledger_status_exit_2(tmp_path: Path, capsys) -> None:
    _seed_status_repo(tmp_path, require="require")
    runner = git_status_runner()
    capsys.readouterr()
    with patch("cli.commands.status.check_governance_freshness", return_value=_OK_FRESHNESS):
        code = run_cli(
            ["status", "--json", "--exit-code"],
            cwd=tmp_path,
            runner=runner,
            json_mode=True,
        )
    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    gate = payload["independent_second_reviewer_gate"]
    assert gate["ok"] is False
    assert gate["token"] == "missing_independent_second_review"


def test_mode_d_cli_with_producer_session_match(tmp_path: Path, capsys) -> None:
    seed_isr_repo(tmp_path, require_independent_second_reviewer="require")
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(load_isr_entry("isr-pass.json")), encoding="utf-8")
    assert (
        run_cli(
            ["ledger", "append", "--kind", "independent_second_review", "--file", "payload.json"],
            cwd=tmp_path,
            runner=git_status_runner(),
            kit=kit_root(),
        )
        == 0
    )
    code = run_cli(
        [
            "honesty-status",
            "--independent-second-review",
            "ISR-b",
            "--producer-session",
            "builder-chat-1",
            "--json",
        ],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["independent_second_review"]["matched_entry_hash"] is not None


def test_same_session_ids_refused_at_append(tmp_path: Path) -> None:
    seed_isr_repo(tmp_path)
    body = load_isr_entry("isr-pass.json")
    body["actor_session_id"] = "same-id"
    body["producer_session_id"] = "same-id"
    payload = tmp_path / "bad.json"
    payload.write_text(json.dumps(body), encoding="utf-8")
    code = run_cli(
        ["ledger", "append", "--kind", "independent_second_review", "--file", "bad.json"],
        cwd=tmp_path,
        runner=git_status_runner(),
        kit=kit_root(),
    )
    assert code == 2


def test_ok_next_still_extracts_fence_after_docs_pointer(tmp_path: Path, capsys) -> None:
    runner = git_status_runner()
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    text = handover.read_text(encoding="utf-8")
    # Ensure paste fence still extractable after pointer-style edit nearby.
    if "Independent second reviewer" not in text:
        text += "\n\nSee docs/INDEPENDENT-SECOND-REVIEWER.md (kit does not run another model).\n"
        handover.write_text(text, encoding="utf-8")
    code = run_cli(["next"], cwd=tmp_path, runner=runner)
    assert code == 0
    out = capsys.readouterr().out
    assert "CURRENT NEXT" in out or "Paste-ready" in out or "```" in out


def test_muse_regime_unsigned_isr_path(tmp_path: Path, capsys) -> None:
    seed_isr_repo(
        tmp_path,
        require_independent_second_reviewer="require",
        regime_config="config-muse-git-mirror.yaml",
    )
    seed_muse_substrate(tmp_path)
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(load_isr_entry("isr-pass.json")), encoding="utf-8")
    assert (
        run_cli(
            ["ledger", "append", "--kind", "independent_second_review", "--file", "payload.json"],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
            kit=kit_root(),
        )
        == 0
    )
    code = run_cli(
        ["honesty-status", "--independent-second-review", "ISR-b", "--json"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
        kit=kit_root(),
        json_mode=True,
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True

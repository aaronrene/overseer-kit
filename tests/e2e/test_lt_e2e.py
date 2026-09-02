"""E2e tests for LT loop tightening (§LT.10)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from tests.support import FIXTURES, KIT_ROOT, git_status_runner, run_cli
from tools.governance_freshness import GovernanceFreshnessReport
from tools.honesty.ledger_io import serialize_entry
from tools.honesty.genesis import build_genesis_entry

_OK_FRESHNESS = GovernanceFreshnessReport(
    state="ok",
    message="patched",
    remediation=None,
    d1="aligned",
    d2="aligned",
    marker_present=True,
)


def _seed_honesty_repo(tmp_path: Path, *, require: str) -> None:
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
  require_verification_evidence: {require}
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
        "| **LT-b Loop tightening build** | Auto | **DONE** | "
        "`docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md` |\n",
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "## NEXT SESSION — LT-b\n\n| | |\n| **ID** | **LT-b** |\n\n"
        "Build verified → `pass` (LT-b-BV-r1).\n",
        encoding="utf-8",
    )


def test_warn_mode_done_without_ledger_status_exit_0(tmp_path: Path, capsys) -> None:
    _seed_honesty_repo(tmp_path, require="warn")
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
    gate = payload.get("verification_evidence_gate")
    assert gate is not None
    assert gate["ok"] is True
    assert gate["mode"] == "warn"
    assert gate["matched"] is False


def test_require_mode_done_without_ledger_status_exit_2(tmp_path: Path, capsys) -> None:
    _seed_honesty_repo(tmp_path, require="require")
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
    gate = payload["verification_evidence_gate"]
    assert gate["ok"] is False
    assert gate["token"] == "missing_verification_evidence"


def _inject_change_log_bullets(handover: Path, count: int) -> None:
    bullets = "\n\n".join(f"- **2026-01-{day:02d}** — entry {day}" for day in range(1, count + 1))
    text = handover.read_text(encoding="utf-8")
    if "<!-- overseer:anchor:change-log -->" in text:
        start = text.index("<!-- overseer:anchor:change-log -->")
        end = text.index("<!-- /overseer:anchor:change-log -->")
        handover.write_text(
            text[: start + len("<!-- overseer:anchor:change-log -->")]
            + "\n"
            + bullets
            + "\n"
            + text[end:],
            encoding="utf-8",
        )
    else:
        handover.write_text(
            text
            + "\n<!-- overseer:anchor:change-log -->\n"
            + bullets
            + "\n<!-- /overseer:anchor:change-log -->\n",
            encoding="utf-8",
        )


def test_compact_then_next_same_fence(tmp_path: Path, capsys) -> None:
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
    _inject_change_log_bullets(handover, 20)
    assert run_cli(["handover-compact", "--write", "--keep", "15"], cwd=tmp_path, runner=runner) == 0
    capsys.readouterr()
    assert run_cli(["next"], cwd=tmp_path, runner=runner) == 0
    after_next = capsys.readouterr().out
    assert "```text" in after_next
    assert "Model:" in after_next

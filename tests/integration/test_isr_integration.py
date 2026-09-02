"""Integration tests for ISR ledger append and Mode D honesty-status (§ISR.11)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import yaml

from tests.fixtures.isr import load_isr_entry, seed_isr_repo
from tests.support import FIXTURES, git_status_runner, run_cli
from tools.governance_freshness import GovernanceFreshnessReport
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.status import (
    EXIT_MISSING_INDEPENDENT_SECOND_REVIEW,
    HonestyStatusOptions,
    run_honesty_status,
)
from tools.honesty.types import LedgerAppendOptions

_OK_FRESHNESS = GovernanceFreshnessReport(
    state="ok",
    message="patched",
    remediation=None,
    d1="aligned",
    d2="aligned",
    marker_present=True,
)


def test_append_isr_writes_chain(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    body = load_isr_entry("isr-pass.json")
    assert (
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="independent_second_review", body=body),
        ).exit_code
        == 0
    )
    assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 0


def test_mode_d_require_missing_exit_38(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="require")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
        ),
    )
    assert result.exit_code == EXIT_MISSING_INDEPENDENT_SECOND_REVIEW
    assert result.json_payload.error == "missing_independent_second_review"
    assert result.json_payload.independent_second_review is not None


def test_mode_d_matching_pass_exit_0(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="require")
    body = load_isr_entry("isr-pass.json")
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
            frozen_spec="docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md",
            producer_session="builder-chat-1",
        ),
    )
    assert result.exit_code == 0
    assert result.json_payload.independent_second_review["matched_entry_hash"] is not None


def test_mode_d_warn_missing_exit_0_with_warning(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="warn")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
        ),
    )
    assert result.exit_code == 0
    assert "warning:" in result.stderr_extra


def test_mode_d_off_not_enforced(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="off")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
        ),
    )
    assert result.exit_code == 0
    assert result.json_payload.independent_second_review["matched_entry_hash"] is None


def test_mode_d_plus_mode_b_exit_1(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
            verification_evidence="phase",
        ),
    )
    assert result.exit_code == 1


def test_mode_d_plus_hook_exit_1(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook="board_done",
            artifact=None,
            independent_second_review="ISR-b",
        ),
    )
    assert result.exit_code == 1


def test_mode_a_without_mode_d_unchanged(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook="board_done",
            artifact="missing.txt",
        ),
    )
    # Module on but artifact missing → refused 4 (pre-ISR Mode A path)
    assert result.exit_code == 4
    assert result.json_payload.independent_second_review is None


def test_honesty_disabled_exit_4(repo_root) -> None:
    config = seed_isr_repo(repo_root, honesty_enabled=False)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            independent_second_review="ISR-b",
        ),
    )
    assert result.exit_code == 4


def _seed_status_fixture(tmp_path: Path, *, require: str) -> None:
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
    from tools.honesty.genesis import build_genesis_entry
    from tools.honesty.ledger_io import serialize_entry

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


def test_status_require_done_without_isr_exit_2(tmp_path: Path, capsys) -> None:
    import json

    _seed_status_fixture(tmp_path, require="require")
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


def test_status_require_after_append_not_forced_2(tmp_path: Path) -> None:
    _seed_status_fixture(tmp_path, require="require")
    cfg_path = tmp_path / ".overseer" / "config.yaml"
    config = __import__("adapters.config", fromlist=["load_config"]).load_config(cfg_path)
    body = load_isr_entry("isr-pass.json")
    append_entry(
        config=config,
        repo_root=tmp_path,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    )
    runner = git_status_runner()
    with patch("cli.commands.status.check_governance_freshness", return_value=_OK_FRESHNESS):
        code = run_cli(
            ["status", "--json", "--exit-code"],
            cwd=tmp_path,
            runner=runner,
            json_mode=True,
        )
    assert code == 0

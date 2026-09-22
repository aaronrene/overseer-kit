"""Integration tests for AFF ledger append and Mode E honesty-status (§AFF.14)."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import yaml

from cli.context import CliContext
from cli.main import main
from cli.output import OutputContext
from tests.fixtures.aff import (
    AFF_FREEZE_REL,
    aff_body,
    current_artifact_digest,
    seed_aff_repo,
    write_mechanical_stamp,
)
from tests.support import git_status_runner, make_runner, ok, seed_governance_freshness
from tools.adversarial_freeze.surface import WARN_ABSENT, build_adversarial_freeze_gate
from tools.honesty.ledger import append_entry, verify_ledger_file
from tools.honesty.status import (
    EXIT_MISSING_ADVERSARIAL_FREEZE,
    HonestyStatusOptions,
    run_honesty_status,
)
from tools.honesty.types import LedgerAppendOptions


def _seed_aff_public_cli_repo(tmp_path: Path, *, mode: str) -> None:
    """Seed an otherwise-green active Auto slice for public CLI assertions."""
    _seed_status_fixture(tmp_path, mode=mode)
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\n"
        "kit_version: 0.1.0\n"
        "config_version: 1\n"
        "installed_at: '2026-01-01T00:00:00Z'\n"
        "synced_at: '2026-01-01T00:00:00Z'\n"
        "footprint_digest: sha256:0\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    seed_governance_freshness(tmp_path)


def _run_aff_cli(tmp_path: Path, argv: list[str], *, runner=None) -> tuple[int, str]:
    stdout = StringIO()
    with patch("sys.stdout", stdout):
        code = main(
            argv,
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=runner or git_status_runner(),
                output=OutputContext(),
            ),
        )
    return code, stdout.getvalue()


def test_append_aff_pass_findings_blocked_round_trips(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)
    for name in ("aff-pass.json", "aff-findings.json", "aff-blocked.json"):
        body = aff_body(name, artifact_digest=digest, actor_session_id=f"adv-{name}")
        assert (
            append_entry(
                config=config,
                repo_root=repo_root,
                options=LedgerAppendOptions(kind="adversarial_freeze", body=body),
            ).exit_code
            == 0
        )
        assert verify_ledger_file(config=config, repo_root=repo_root).exit_code == 0


def test_mode_e_require_no_match_exit_40(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    write_mechanical_stamp(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result.exit_code == EXIT_MISSING_ADVERSARIAL_FREEZE
    assert result.json_payload.error == "missing_adversarial_freeze"
    block = result.json_payload.adversarial_freeze
    assert block is not None
    assert block["mode"] == "require"
    assert block["matched_via"] is None
    assert block["matched_entry_hash"] is None


def test_mode_e_matching_pass_exit_0_exact_block(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)
    body = aff_body(artifact_digest=digest)
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="adversarial_freeze", body=body),
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
            producer_session="aff-a-author-session",
        ),
    )
    assert result.exit_code == 0
    block = result.json_payload.adversarial_freeze
    assert block is not None
    assert block["matched_via"] == "pass"
    assert block["matched_entry_hash"] is not None
    assert block["frozen_spec"] == AFF_FREEZE_REL
    assert block["artifact_digest"] == digest
    assert block["mode"] == "require"
    assert result.json_payload.independent_second_review is None
    assert result.json_payload.verification_evidence is None


def test_mode_e_suggest_miss_warns(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    write_mechanical_stamp(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result.exit_code == 0
    assert "warning:" in result.stderr_extra


def test_mode_e_off_exact_block_no_ledger_read(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="off")
    write_mechanical_stamp(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result.exit_code == 0
    block = result.json_payload.adversarial_freeze
    assert block is not None
    assert block["mode"] == "off"
    assert block["matched_via"] is None
    assert block["matched_entry_hash"] is None


def test_mode_e_plus_mode_d_exit_1(repo_root) -> None:
    config = seed_aff_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            independent_second_review="ISR-b",
        ),
    )
    assert result.exit_code == 1


def test_aff_mode_e_cli_parser_command_path(repo_root: Path) -> None:
    """Mode E must be reached through ``ok honesty-status`` argument wiring."""
    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)

    missing_code, missing_stdout = _run_aff_cli(
        repo_root,
        [
            "--json",
            "honesty-status",
            "--adversarial-freeze",
            "AFF",
            "--frozen-spec",
            AFF_FREEZE_REL,
            "--artifact-digest",
            digest,
        ],
    )
    assert missing_code == EXIT_MISSING_ADVERSARIAL_FREEZE
    missing = json.loads(missing_stdout)
    assert missing["error"] == "missing_adversarial_freeze"
    assert missing["adversarial_freeze"]["matched_via"] is None

    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body(artifact_digest=digest),
        ),
    )
    passed_code, passed_stdout = _run_aff_cli(
        repo_root,
        [
            "--json",
            "honesty-status",
            "--adversarial-freeze",
            "AFF",
            "--frozen-spec",
            AFF_FREEZE_REL,
            "--artifact-digest",
            digest,
        ],
    )
    assert passed_code == 0
    assert json.loads(passed_stdout)["adversarial_freeze"]["matched_via"] == "pass"

    usage_code, _ = _run_aff_cli(
        repo_root,
        [
            "honesty-status",
            "--adversarial-freeze",
            "AFF",
            "--verification-evidence",
            "AFF-b",
        ],
    )
    assert usage_code == 1


def test_mode_e_digest_without_frozen_usage_1(repo_root) -> None:
    config = seed_aff_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            artifact_digest="sha256:" + ("a" * 64),
        ),
    )
    assert result.exit_code == 1


def test_mode_e_malformed_digest_usage_1(repo_root) -> None:
    config = seed_aff_repo(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
            artifact_digest="sha256:not-hex",
        ),
    )
    assert result.exit_code == 1


def test_mode_e_digest_mismatch_usage_1(repo_root) -> None:
    config = seed_aff_repo(repo_root)
    write_mechanical_stamp(repo_root)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
            artifact_digest="sha256:" + ("b" * 64),
        ),
    )
    assert result.exit_code == 1


def test_mode_e_non_regular_frozen_spec_plus_digest(repo_root) -> None:
    config = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest = "sha256:" + ("c" * 64)
    # directory path under repo
    docs_dir = "docs"
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=docs_dir,
            artifact_digest=digest,
        ),
    )
    # Mode E explicit ledger query — not usage 1, not refusal 4
    assert result.exit_code in {0, EXIT_MISSING_ADVERSARIAL_FREEZE}
    assert result.exit_code != 1
    assert result.exit_code != 4
    block = result.json_payload.adversarial_freeze
    assert block is not None
    assert block["frozen_spec"] == docs_dir
    assert block["artifact_digest"] == digest


def test_honesty_disabled_exit_4(repo_root) -> None:
    config = seed_aff_repo(repo_root, honesty_enabled=False)
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert result.exit_code == 4


def test_skip_authorizes_under_suggest_not_require(repo_root) -> None:
    config_s = seed_aff_repo(repo_root, adversarial_freeze="suggest")
    digest_s = write_mechanical_stamp(repo_root)
    skip = aff_body("aff-skip.json", artifact_digest=digest_s)
    append_entry(
        config=config_s,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="adversarial_freeze", body=skip),
    )
    ok = run_honesty_status(
        config=config_s,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert ok.exit_code == 0
    assert ok.json_payload.adversarial_freeze["matched_via"] == "skip"

    # require: same skip is inert → miss
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["adversarial_freeze"] = "require"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    from adapters.config import load_config

    config_r = load_config(cfg_path)
    miss = run_honesty_status(
        config=config_r,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            adversarial_freeze="AFF",
            frozen_spec=AFF_FREEZE_REL,
        ),
    )
    assert miss.exit_code == EXIT_MISSING_ADVERSARIAL_FREEZE


def _seed_status_fixture(tmp_path: Path, *, mode: str) -> None:
    """Seed Auto-slice AFF status fixture without ``ok init`` (sandbox-safe)."""
    from adapters.config import load_config
    from tools.honesty.genesis import build_genesis_entry
    from tools.honesty.ledger_io import serialize_entry

    config = seed_aff_repo(tmp_path, adversarial_freeze=mode)
    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["honesty"]["adversarial_freeze"] = mode
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(cfg)

    ledger_dir = tmp_path / ".overseer" / "honesty"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    if not (ledger_dir / "VERDICT-LEDGER.jsonl").is_file():
        genesis = serialize_entry(build_genesis_entry("2026-01-01T00:00:00Z"))
        (ledger_dir / "VERDICT-LEDGER.jsonl").write_text(genesis + "\n", encoding="utf-8")

    digest = write_mechanical_stamp(tmp_path)
    append_entry(
        config=config,
        repo_root=tmp_path,
        options=LedgerAppendOptions(
            kind="freeze_review",
            body={
                "actor_role": "verifier",
                "actor_session_id": "frv-1",
                "phase_id": "AFF-b",
                "frozen_spec": AFF_FREEZE_REL,
                "round": 1,
                "gate": "substantive",
                "freeze_verdict": "pass",
                "artifact_digest": digest,
                "reviewer_model": "thinking-high",
            },
        ),
    )
    docs = tmp_path / "docs"
    (docs / "ROADMAP.md").write_text(
        "# Roadmap\n\n## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        f"| **AFF-b Adversarial freeze build** | Auto | **WIP** | "
        f"`{AFF_FREEZE_REL}` |\n",
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "## NEXT SESSION — AFF-b\n\n| | |\n| **ID** | **AFF-b** |\n\n",
        encoding="utf-8",
    )


def _aff_governance_runner():
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
        }
    )


def test_aff_public_status_and_governance_require_miss_then_pass(tmp_path: Path) -> None:
    """Run the public status and governance commands, not just their AFF helper."""
    _seed_aff_public_cli_repo(tmp_path, mode="require")
    from adapters.config import load_config

    missing_code, missing_stdout = _run_aff_cli(
        tmp_path, ["--json", "status", "--exit-code"]
    )
    missing = json.loads(missing_stdout)
    assert missing_code == 2
    assert missing["adversarial_freeze_gate"]["token"] == "missing_adversarial_freeze"
    assert missing["adversarial_freeze_gate"]["state"] == "pending"

    governance_code, governance_stdout = _run_aff_cli(
        tmp_path, ["governance-sync"], runner=_aff_governance_runner()
    )
    assert governance_code == 2
    assert "missing adversarial_freeze" in governance_stdout

    config = load_config(tmp_path / ".overseer" / "config.yaml")
    append_entry(
        config=config,
        repo_root=tmp_path,
        options=LedgerAppendOptions(
            kind="adversarial_freeze",
            body=aff_body(artifact_digest=current_artifact_digest(tmp_path)),
        ),
    )
    passed_code, passed_stdout = _run_aff_cli(
        tmp_path, ["--json", "status", "--exit-code"]
    )
    passed = json.loads(passed_stdout)
    assert passed_code == 0
    assert passed["adversarial_freeze_gate"]["ok"] is True
    assert passed["adversarial_freeze_gate"]["state"] == "pass"


def test_aff_public_governance_sync_suggest_pending_and_absent(tmp_path: Path) -> None:
    """Public status JSON + governance-sync for suggest pending and absent (§AFF.14)."""
    _seed_aff_public_cli_repo(tmp_path, mode="suggest")

    pending_status_code, pending_status_stdout = _run_aff_cli(
        tmp_path, ["--json", "status", "--exit-code"]
    )
    pending_status = json.loads(pending_status_stdout)
    assert pending_status_code == 0
    assert "adversarial_freeze_gate" in pending_status
    assert pending_status["adversarial_freeze_gate"]["state"] == "pending"
    assert pending_status["adversarial_freeze_gate"]["ok"] is True
    assert pending_status["adversarial_freeze_gate"]["mode"] == "suggest"
    assert (
        "warning: no authorizing adversarial_freeze entry for active Auto slice"
        in pending_status["warnings"]
    )

    pending_code, pending_stdout = _run_aff_cli(
        tmp_path, ["governance-sync"], runner=_aff_governance_runner()
    )
    assert pending_code == 0
    assert "warning: no authorizing adversarial_freeze entry for active Auto slice" in pending_stdout

    ledger = tmp_path / ".overseer" / "honesty" / "VERDICT-LEDGER.jsonl"
    ledger.write_text("not-json\n", encoding="utf-8")
    with patch(
        "tools.adversarial_freeze.surface.frv_authorizing_freeze_paths",
        return_value=[tmp_path / AFF_FREEZE_REL],
    ):
        absent_status_code, absent_status_stdout = _run_aff_cli(
            tmp_path, ["--json", "status", "--exit-code"]
        )
        absent_code, absent_stdout = _run_aff_cli(
            tmp_path, ["governance-sync"], runner=_aff_governance_runner()
        )
    absent_status = json.loads(absent_status_stdout)
    assert absent_status_code == 0
    assert "adversarial_freeze_gate" in absent_status
    assert absent_status["adversarial_freeze_gate"]["state"] == "absent"
    assert absent_status["adversarial_freeze_gate"]["ok"] is True
    assert absent_status["adversarial_freeze_gate"]["mode"] == "suggest"
    assert absent_status["adversarial_freeze_gate"]["matched"] is False
    assert WARN_ABSENT in absent_status["warnings"]
    assert absent_code == 0
    assert WARN_ABSENT in absent_stdout


def test_mixed_candidate_aggregate_parity(repo_root) -> None:
    from tools.adversarial_freeze import aggregate_adversarial_authorization_states
    from tools.governance_hygiene.next_regen import decide_split_emission, _apply_adversarial_freeze_hold
    from tools.governance_hygiene.types import QueueRow

    config = seed_aff_repo(repo_root, adversarial_freeze="require")
    digest = write_mechanical_stamp(repo_root)
    append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(
            kind="freeze_review",
            body={
                "actor_role": "verifier",
                "actor_session_id": "frv-1",
                "phase_id": "AFF-b",
                "frozen_spec": AFF_FREEZE_REL,
                "round": 1,
                "gate": "substantive",
                "freeze_verdict": "pass",
                "artifact_digest": digest,
                "reviewer_model": "thinking-high",
            },
        ),
    )
    # no AFF → pending hold on Auto
    auto_row = QueueRow(
        phase_label="**AFF-b**",
        model="Auto",
        status="**NEXT**",
        deliverable=f"`{AFF_FREEZE_REL}`",
        raw_line="",
    )
    emit, reason, is_b, advisory = decide_split_emission(auto_row, repo_root, config=config)
    assert emit == "Auto"
    emit2, is_b2, adv2 = _apply_adversarial_freeze_hold(
        row=auto_row,
        repo_root=repo_root,
        config=config,
        emit_model=emit,
        is_step_b=is_b,
        advisory=advisory,
        step_id="AFF-b",
    )
    assert emit2 == "Thinking"
    assert adv2 == "adversarial_freeze_pending"

    gate = build_adversarial_freeze_gate(
        config,
        repo_root,
        handover_text="## NEXT\n| **ID** | **AFF-b** |\n",
        roadmap_text=(
            "# Roadmap\n\n## Build queue\n\n"
            "| Phase | Model | Status | Deliverable |\n"
            "| --- | --- | --- | --- |\n"
            f"| **AFF-b** | Auto | **WIP** | `{AFF_FREEZE_REL}` |\n"
        ),
    )
    assert gate.state == "pending"
    assert gate.ok is False

    # pass then aggregate ranks
    assert aggregate_adversarial_authorization_states(["pass", "pending"]) == "pending"
    assert aggregate_adversarial_authorization_states(["pass", "absent"]) == "absent"
    assert aggregate_adversarial_authorization_states(["pass", "skipped"]) == "skipped"

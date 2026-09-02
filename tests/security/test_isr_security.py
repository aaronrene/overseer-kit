"""Security tests for ISR opaque session ids and role gates (§ISR.11)."""

from __future__ import annotations

import inspect

from tests.fixtures.isr import load_isr_entry, seed_isr_repo
from tools.honesty.ledger import append_entry
from tools.honesty.status import (
    EXIT_MISSING_INDEPENDENT_SECOND_REVIEW,
    HonestyStatusOptions,
    run_honesty_status,
)
from tools.honesty.types import LedgerAppendOptions
from tools.independent_second_reviewer import (
    build_independent_second_reviewer_gate,
    independent_second_reviewer_gate_payload,
)


def test_url_like_session_ids_opaque(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    body = load_isr_entry("isr-pass.json")
    body["actor_session_id"] = "https://evil.example/$(curl)"
    body["producer_session_id"] = "file:///etc/passwd; rm -rf /"
    body["notes"] = "https://example.com/hook?x=`id`"
    code = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    ).exit_code
    assert code == 0


def test_no_network_or_model_imports_on_isr_paths() -> None:
    import tools.honesty.ledger as ledger_mod
    import tools.honesty.status as status_mod
    import tools.honesty.validate as validate_mod
    import tools.independent_second_reviewer.surface as surface_mod

    for module in (ledger_mod, status_mod, validate_mod, surface_mod):
        source = inspect.getsource(module)
        assert "urllib" not in source
        assert "requests" not in source
        assert "httpx" not in source
        assert "openai" not in source
        assert "anthropic" not in source


def test_producer_cannot_append_isr(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    body = load_isr_entry("isr-producer.json")
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    )
    assert result.exit_code == 23


def test_equal_session_ids_cannot_pass(repo_root) -> None:
    config = seed_isr_repo(repo_root)
    body = load_isr_entry("isr-pass.json")
    body["actor_session_id"] = "same"
    body["producer_session_id"] = "same"
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="independent_second_review", body=body),
    )
    assert result.exit_code == 2


def test_exit_38_not_waived_under_require(repo_root) -> None:
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


def test_gate_payload_no_absolute_machine_paths(repo_root) -> None:
    config = seed_isr_repo(repo_root, require_independent_second_reviewer="require")
    report = build_independent_second_reviewer_gate(
        config,
        repo_root,
        handover_text=(
            "## NEXT SESSION — ISR-b\n\n| | |\n| **ID** | **ISR-b** |\n\n"
            "Build verified → `pass` (ISR-b-BV-r1).\n"
        ),
        roadmap_text=(
            "| Phase | Model | Status | Deliverable |\n"
            "| --- | --- | --- | --- |\n"
            "| **ISR-b Independent second reviewer build** | Auto | **DONE** | "
            "`docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md` |\n"
        ),
    )
    payload = independent_second_reviewer_gate_payload(report)
    assert payload is not None
    blob = str(payload)
    assert "/Users/" not in blob
    assert "C:\\" not in blob

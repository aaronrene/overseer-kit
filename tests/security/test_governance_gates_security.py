"""Security tests for governance gate scan (path safety, no shell)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import ConfigError, load_config
from tests.support import FIXTURES


def test_governance_gates_surfaces_reject_unknown_entries(tmp_path: Path) -> None:
    base = (FIXTURES / "config-governance-gates.yaml").read_text(encoding="utf-8")
    bad = base.replace(
        "    - handover-paste",
        "    - handover-paste\n    - exec-malicious",
    )
    path = tmp_path / "bad.yaml"
    path.write_text(bad, encoding="utf-8")
    try:
        load_config(path)
        raised = False
    except ConfigError:
        raised = True
    assert raised


def test_scan_does_not_follow_path_escape_contract(tmp_path: Path) -> None:
    from tools.governance_gates import scan_governance_gates

    config = load_config(FIXTURES / "config-governance-gates.yaml")
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "ROADMAP.md").write_text(
        "| **Escape** | Thinking | **WIP** | `../../../etc/passwd` |\n",
        encoding="utf-8",
    )
    (docs / "OVERSEER-HANDOVER.md").write_text("| **ID** | **Escape** |\n", encoding="utf-8")
    result = scan_governance_gates(config, tmp_path)
    assert all("passwd" not in (gate.artifact or "") for gate in result.pending)

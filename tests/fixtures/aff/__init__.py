"""AFF fixture helpers (§AFF.14)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from adapters.config import OverseerConfig, load_config
from tests.support import seed_honesty_repo, seed_muse_substrate

FIXTURES = Path(__file__).resolve().parent
AFF_ENTRIES = FIXTURES / "entries"
AFF_FREEZE_REL = "docs/archive/phases/PHASE-AFF-ADVERSARIAL-FREEZE-HONESTY-GATE.md"
AFF_DIGEST_PLACEHOLDER = "sha256:" + ("a" * 64)


def load_aff_entry(name: str) -> dict:
    """Load an adversarial_freeze entry fixture by filename."""
    return json.loads((AFF_ENTRIES / name).read_text(encoding="utf-8"))


def seed_aff_repo(
    repo_root: Path,
    *,
    adversarial_freeze: str | None = "suggest",
    honesty_enabled: bool = True,
    human_escalation: list[str] | None = None,
    omit_adversarial_freeze_key: bool = False,
    regime_config: str | None = None,
    write_freeze_artifact: bool = True,
) -> OverseerConfig:
    """Seed honesty repo with AFF gate config and archive freeze path."""
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["enabled"] = honesty_enabled
    if omit_adversarial_freeze_key:
        data["honesty"].pop("adversarial_freeze", None)
    elif adversarial_freeze is not None:
        data["honesty"]["adversarial_freeze"] = adversarial_freeze
    escalation = human_escalation if human_escalation is not None else ["security"]
    data["freeze_contract"] = {
        "enabled": True,
        "reviewer": {
            "mode": "agent",
            "model": "thinking-high",
            "provider": "local",
            "fallback": "human",
        },
        "human_escalation": list(escalation),
    }
    if "modules" in data and isinstance(data["modules"], dict):
        honesty_mod = data["modules"].setdefault("honesty", {})
        if isinstance(honesty_mod, dict):
            honesty_mod["enabled"] = honesty_enabled
    if regime_config is not None:
        regime_src = Path(__file__).resolve().parents[2] / "fixtures" / Path(regime_config).name
        regime_data = yaml.safe_load(regime_src.read_text(encoding="utf-8"))
        for key in ("vcs", "repo", "docs", "thresholds", "freeze_contract"):
            if key in regime_data:
                data[key] = regime_data[key]
        data["freeze_contract"] = {
            **data.get("freeze_contract", {}),
            "enabled": True,
            "human_escalation": list(escalation),
        }
        if regime_data.get("vcs", {}).get("regime", "").startswith("muse"):
            seed_muse_substrate(repo_root)
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    archive = docs / "archive" / "phases"
    archive.mkdir(parents=True, exist_ok=True)
    if write_freeze_artifact:
        art = repo_root / AFF_FREEZE_REL
        if not art.is_file():
            art.write_text(
                "# AFF freeze\n\n"
                "```yaml\n"
                "phase: AFF\n"
                "outputs:\n"
                "  - id: a\n"
                "    path: docs/a.md\n"
                "    frozen: true\n"
                "```\n\n"
                "Ground truth frozen: true. seven-tier matrix. file+line citation.\n",
                encoding="utf-8",
            )
    return load_config(cfg_path)


def copy_aff_entries(repo_root: Path) -> None:
    """Copy entry fixtures into repo for CLI append tests."""
    dest = repo_root / "entries"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(AFF_ENTRIES, dest)


def aff_body(
    name: str = "aff-pass.json",
    *,
    artifact_digest: str | None = None,
    **overrides,
) -> dict:
    """Load fixture and optionally override digest / fields."""
    body = load_aff_entry(name)
    if artifact_digest is not None:
        body["artifact_digest"] = artifact_digest
    body.update(overrides)
    return body


def write_mechanical_stamp(repo_root: Path, rel: str = AFF_FREEZE_REL) -> str:
    """Stamp freeze artifact mechanically; return current artifact_digest."""
    from tools.freeze_reviewer.artifact import artifact_digest, parse_artifact
    from tools.freeze_reviewer.stamp import build_stamp, write_stamp
    from tools.freeze_reviewer.types import ReviewerSettings

    path = repo_root / rel
    parsed = parse_artifact(path, rel_path=rel)
    stamp = build_stamp(
        parsed,
        reviewer=ReviewerSettings("agent", "thinking-high", "local", "human"),
        kit_version="0.1.0",
        produced_by="checklist_engine",
        provider_kind="rule_engine",
        checklist_ids=["C1"],
        checklist_source="builtin",
        findings_count=0,
    )
    write_stamp(path, parsed, stamp)
    reparsed = parse_artifact(path, rel_path=rel)
    return artifact_digest(reparsed)


def current_artifact_digest(repo_root: Path, rel: str = AFF_FREEZE_REL) -> str:
    """Return FRV artifact_digest for the freeze path."""
    from tools.freeze_reviewer.artifact import artifact_digest, parse_artifact

    path = repo_root / rel
    return artifact_digest(parse_artifact(path, rel_path=rel))

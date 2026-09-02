"""ISR fixture helpers (§ISR.11)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from adapters.config import OverseerConfig, load_config
from tests.support import seed_honesty_repo

FIXTURES = Path(__file__).resolve().parent
ISR_ENTRIES = FIXTURES / "entries"


def load_isr_entry(name: str) -> dict:
    """Load an independent_second_review entry fixture."""
    return json.loads((ISR_ENTRIES / name).read_text(encoding="utf-8"))


def seed_isr_repo(
    repo_root: Path,
    *,
    require_independent_second_reviewer: str = "off",
    require_verification_evidence: str = "off",
    honesty_enabled: bool = True,
    regime_config: str | None = None,
) -> OverseerConfig:
    """Seed honesty repo with optional ISR gate config."""
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["enabled"] = honesty_enabled
    data["honesty"]["require_independent_second_reviewer"] = require_independent_second_reviewer
    data["honesty"]["require_verification_evidence"] = require_verification_evidence
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
        if regime_data.get("vcs", {}).get("regime", "").startswith("muse"):
            from tests.support import seed_muse_substrate

            seed_muse_substrate(repo_root)
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "archive" / "phases").mkdir(parents=True, exist_ok=True)
    (
        docs / "archive" / "phases" / "PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md"
    ).write_text("# frozen isr\n", encoding="utf-8")
    return load_config(cfg_path)


def copy_isr_entries(repo_root: Path) -> None:
    """Copy entry fixtures into repo for CLI append tests."""
    dest = repo_root / "entries"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ISR_ENTRIES, dest)

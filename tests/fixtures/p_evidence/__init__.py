"""P-evidence fixture helpers (§PE.10)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from adapters.config import OverseerConfig, load_config
from tests.support import HONESTY, seed_honesty_repo

FIXTURES = Path(__file__).resolve().parent
P_EVIDENCE_ENTRIES = FIXTURES / "entries"


def load_p_evidence_entry(name: str) -> dict:
    """Load a verification_evidence entry fixture."""
    return json.loads((P_EVIDENCE_ENTRIES / name).read_text(encoding="utf-8"))


def seed_p_evidence_repo(
    repo_root: Path,
    *,
    require_verification_evidence: str = "off",
    regime_config: str | None = None,
) -> OverseerConfig:
    """Seed honesty repo with optional verification-evidence config."""
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["honesty"]["require_verification_evidence"] = require_verification_evidence
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
    (docs / "PHASE-TRACK-P-P-EVIDENCE.md").write_text("# frozen spec\n", encoding="utf-8")
    archive = repo_root / "docs" / "archive" / "verify"
    archive.mkdir(parents=True, exist_ok=True)
    (archive / "p-evidence-status.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
    return load_config(cfg_path)


def copy_p_evidence_entries(repo_root: Path) -> None:
    """Copy entry fixtures into repo for CLI append tests."""
    dest = repo_root / "entries"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(P_EVIDENCE_ENTRIES, dest)

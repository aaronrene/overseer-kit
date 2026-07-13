"""Integration tests for built-in checkpoint orchestrator."""

from __future__ import annotations

from pathlib import Path

import yaml

from tests.support import load_checkpoint_config, seed_checkpoint_repo
from tools.checkpoints.orchestrator import VerifyStepOptions, run_verify_step


def test_step_pass_updates_manifest(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha"),
    )
    assert result.exit_code == 0
    manifest = yaml.safe_load((repo_root / "manifests" / "work-unit.yaml").read_text(encoding="utf-8"))
    assert manifest["steps"]["alpha"]["verified"] is True
    assert manifest["current_step"] == "beta"
    progress = (repo_root / "PROGRESS.md").read_text(encoding="utf-8")
    assert "alpha" in progress


def test_verify_fail_exit_10_no_write(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    manifest_path = repo_root / "manifests" / "work-unit.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    data["template_id"] = "three_step"
    data["current_step"] = "gamma"
    data["steps"]["alpha"]["verified"] = True
    data["steps"]["beta"]["verified"] = True
    data["steps"]["gamma"] = {
        "verified": False,
        "verified_at": None,
        "artifact_sha256": None,
    }
    manifest_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    from adapters.config import load_config

    config = load_config(repo_root / ".overseer" / "config.yaml")
    before = manifest_path.read_bytes()
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="gamma"),
    )
    assert result.exit_code == 10
    assert manifest_path.read_bytes() == before


def test_artifact_sha256_persisted(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha"),
    )
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="beta"),
    )
    assert result.exit_code == 0
    manifest = yaml.safe_load((repo_root / "manifests" / "work-unit.yaml").read_text(encoding="utf-8"))
    assert manifest["steps"]["beta"]["artifact_sha256"] == "abcdef0123456789"

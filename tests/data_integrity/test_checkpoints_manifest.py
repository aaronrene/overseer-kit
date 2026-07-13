"""Data-integrity tests for checkpoint manifest writes."""

from __future__ import annotations

import yaml

from tests.support import load_checkpoint_config, seed_checkpoint_repo
from tools.checkpoints.orchestrator import VerifyStepOptions, run_verify_step


def test_idempotent_reverify(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    assert run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha"),
    ).exit_code == 0
    after_first = (repo_root / "manifests" / "work-unit.yaml").read_text(encoding="utf-8")
    assert run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha"),
    ).exit_code == 0
    after_second = (repo_root / "manifests" / "work-unit.yaml").read_text(encoding="utf-8")
    data1 = yaml.safe_load(after_first)
    data2 = yaml.safe_load(after_second)
    assert data1["steps"]["alpha"]["verified"] is True
    assert data2["steps"]["alpha"]["verified"] is True


def test_mid_through_fail_keeps_prior_writes(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    manifest_path = repo_root / "manifests" / "work-unit.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    data["template_id"] = "three_step"
    data["current_step"] = "gamma"
    data["steps"]["gamma"] = {"verified": False, "verified_at": None, "artifact_sha256": None}
    manifest_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    from adapters.config import load_config

    config = load_config(repo_root / ".overseer" / "config.yaml")
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(through_current=True),
    )
    assert result.exit_code == 10
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["steps"]["alpha"]["verified"] is True
    assert manifest["steps"]["beta"]["verified"] is True
    assert manifest["steps"]["gamma"]["verified"] is False


def test_dry_run_writes_nothing(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    manifest_path = repo_root / "manifests" / "work-unit.yaml"
    progress_path = repo_root / "PROGRESS.md"
    before_manifest = manifest_path.read_bytes()
    code = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(verify_all=True, dry_run=True),
    ).exit_code
    assert code == 0
    assert manifest_path.read_bytes() == before_manifest
    assert not progress_path.exists()

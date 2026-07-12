"""Unit tests for K9b checkpoint config, schema, and orchestrator helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from adapters.errors import ConfigError
from tests.support import CHECKPOINTS, load_checkpoint_config, seed_checkpoint_repo, write_config
from tools.checkpoints.advance import compute_advance
from tools.checkpoints.artifact_hash import parse_artifact_sha256
from tools.checkpoints.argv_builder import build_verify_argv
from tools.checkpoints.executor import ExecResult, RecordingScriptExecutor
from tools.checkpoints.ids import is_valid_step_id
from tools.checkpoints.orchestrator import VerifyStepOptions, run_verify_step
from tools.checkpoints.schema import CheckpointSchemaError, load_manifest, load_policy, resolve_template_steps


def test_step_id_regex() -> None:
    assert is_valid_step_id("alpha")
    assert is_valid_step_id("a1_b-2")
    assert not is_valid_step_id("Alpha")
    assert not is_valid_step_id("")


def test_artifact_sha256_trailing_newlines() -> None:
    assert parse_artifact_sha256(b"line\nARTIFACT_SHA256=AbCdEf\n\n") == "abcdef"
    assert parse_artifact_sha256(b"ARTIFACT_SHA256=ff00") == "ff00"
    assert parse_artifact_sha256(b"no hash here") is None
    assert parse_artifact_sha256(b"\xff\xfe") is None


def test_argv_builder_always_includes_policy() -> None:
    argv = build_verify_argv(
        verify_script="scripts/verify/verify_alpha.py",
        manifest_rel="manifests/work-unit.yaml",
        step_id="alpha",
        policy_rel="policy/checkpoints.yaml",
    )
    assert argv == [
        "scripts/verify/verify_alpha.py",
        "--manifest",
        "manifests/work-unit.yaml",
        "--step",
        "alpha",
        "--policy",
        "policy/checkpoints.yaml",
    ]


def test_current_step_advance() -> None:
    steps = ["alpha", "beta", "gamma"]
    verified = {"alpha": True, "beta": False, "gamma": False}
    assert compute_advance(steps, "alpha", verified, "alpha") == "beta"
    verified["beta"] = True
    assert compute_advance(steps, "beta", verified, "beta") == "gamma"
    verified["gamma"] = True
    assert compute_advance(steps, "gamma", verified, "gamma") == "gamma"


def test_checkpoints_config_mirror_mismatch_raises(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["modules"]["checkpoints"]["enabled"] = False
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="must equal checkpoints.enabled"):
        load_config(cfg_path)


def test_governance_disabled_raises(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["modules"]["governance"]["enabled"] = False
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="governance.enabled cannot be false"):
        load_config(cfg_path)


def test_extensions_well_formed_warn_only(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["extensions"] = [{"id": "future", "schema_version": 1, "config_path": "ext.yaml"}]
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    cfg = load_config(cfg_path)
    assert cfg.extensions
    assert cfg.extension_warnings


def test_extensions_malformed_raises(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data["extensions"] = [{"id": "x"}]
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="schema_version"):
        load_config(cfg_path)


def test_policy_version_not_one_raises(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    policy_path = repo_root / "policy" / "checkpoints.yaml"
    data = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    data["version"] = 2
    policy_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(CheckpointSchemaError, match="version must be integer 1"):
        load_policy(policy_path)


def test_unused_broken_template_not_validated_until_selected(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    policy = load_policy(repo_root / "policy" / "checkpoints.yaml")
    manifest = load_manifest(repo_root / "manifests" / "work-unit.yaml")
    steps = resolve_template_steps(policy, manifest)
    assert steps == ["alpha", "beta"]


def test_step_not_in_template_refused(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="gamma", emit_json=True),
    )
    assert result.exit_code == 2


def test_current_step_not_in_template_refused(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    manifest_path = repo_root / "manifests" / "work-unit.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    data["current_step"] = "gamma"
    manifest_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(repo_root / ".overseer" / "config.yaml")
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha", emit_json=True),
    )
    assert result.exit_code == 2


def test_missing_manifest_step_refused(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    manifest_path = repo_root / "manifests" / "work-unit.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    del data["steps"]["beta"]
    manifest_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(repo_root / ".overseer" / "config.yaml")
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha", emit_json=True),
    )
    assert result.exit_code == 2


def test_checkpoints_disabled_refused_without_manifest(repo_root: Path) -> None:
    write_config(repo_root, "config-git-only.yaml")
    config = load_config(repo_root / ".overseer" / "config.yaml")
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha", emit_json=True),
    )
    assert result.exit_code == 4


def test_dry_run_no_writes(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    manifest_path = repo_root / "manifests" / "work-unit.yaml"
    before = manifest_path.read_bytes()
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha", dry_run=True, emit_json=True),
    )
    assert result.exit_code == 0
    assert result.json_payload.dry_run is True
    assert manifest_path.read_bytes() == before


def test_json_dry_run_echo_on_empty_through(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    shutil_copy = CHECKPOINTS / "manifests" / "all-verified.yaml"
    (repo_root / "manifests" / "work-unit.yaml").write_text(
        shutil_copy.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    config = load_config(repo_root / ".overseer" / "config.yaml")
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(through_current=True, dry_run=True, emit_json=True),
    )
    assert result.exit_code == 0
    assert result.json_payload.dry_run is True
    assert result.json_payload.steps == []


def test_orchestrator_missing_refused(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    config_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    data["checkpoints"]["orchestrator"] = "scripts/missing-orchestrator.sh"
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(config_path)
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha", emit_json=True),
    )
    assert result.exit_code == 4


def test_manifest_write_io_exit_5(repo_root: Path) -> None:
    config = load_checkpoint_config(repo_root)
    executor = RecordingScriptExecutor(
        responses={
            (
                "scripts/verify/verify_alpha.py",
                "--manifest",
                "manifests/work-unit.yaml",
                "--step",
                "alpha",
                "--policy",
                "policy/checkpoints.yaml",
            ): ExecResult(stdout=b"", stderr=b"", exit_code=0),
        },
        calls=[],
    )

    def fail_write(_path: Path, _text: str) -> None:
        from cli.atomic import WriteFailure

        raise WriteFailure(_path, OSError("disk full"))

    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(step_id="alpha", emit_json=True),
        executor=executor,
        write_manifest=fail_write,
    )
    assert result.exit_code == 5
    assert result.json_payload.error == "io"

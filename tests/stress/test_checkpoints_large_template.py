"""Stress tests for checkpoint orchestrator."""

from __future__ import annotations

import stat
from pathlib import Path

import yaml

from tests.support import seed_checkpoint_repo
from tools.checkpoints.orchestrator import VerifyStepOptions, run_verify_step
from adapters.config import load_config


def _write_large_template(repo_root: Path, step_count: int = 100) -> None:
    policy_path = repo_root / "policy" / "checkpoints.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    steps = {}
    template_steps = []
    scripts_dir = repo_root / "scripts" / "verify"
    for index in range(step_count):
        step_id = f"s{index:03d}"
        script_name = f"verify_{step_id}.py"
        script_path = scripts_dir / script_name
        script_path.write_text(
            "#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n",
            encoding="utf-8",
        )
        script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR)
        steps[step_id] = {"verify_script": f"scripts/verify/{script_name}"}
        template_steps.append(step_id)
    policy["steps"].update(steps)
    policy["templates"]["large"] = {"steps": template_steps}
    policy["overrides"]["large"] = {f"k{i}": f"v{i}" for i in range(200)}
    policy_path.write_text(yaml.safe_dump(policy), encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "template_id": "large",
        "slug": "stress",
        "current_step": template_steps[0],
        "meta": {},
        "steps": {
            sid: {"verified": False, "verified_at": None, "artifact_sha256": None}
            for sid in template_steps
        },
    }
    (repo_root / "manifests" / "work-unit.yaml").write_text(
        yaml.safe_dump(manifest),
        encoding="utf-8",
    )


def test_hundred_step_template_dry_run(repo_root: Path) -> None:
    seed_checkpoint_repo(repo_root)
    _write_large_template(repo_root, 100)
    config = load_config(repo_root / ".overseer" / "config.yaml")
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(verify_all=True, dry_run=True),
    )
    assert result.exit_code == 0

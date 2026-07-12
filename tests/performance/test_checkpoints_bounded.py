"""Performance bounds for checkpoint verify-step."""

from __future__ import annotations

import stat
import time

import yaml

from adapters.config import load_config
from tests.support import seed_checkpoint_repo
from tools.checkpoints.orchestrator import VerifyStepOptions, run_verify_step


def _seed_twenty_step(repo_root) -> None:
    seed_checkpoint_repo(repo_root)
    policy_path = repo_root / "policy" / "checkpoints.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    steps = {}
    template_steps = []
    for index in range(20):
        step_id = f"p{index:02d}"
        script_name = f"verify_{step_id}.py"
        script_path = repo_root / "scripts" / "verify" / script_name
        script_path.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", encoding="utf-8")
        script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR)
        steps[step_id] = {"verify_script": f"scripts/verify/{script_name}"}
        template_steps.append(step_id)
    policy["steps"].update(steps)
    policy["templates"]["perf"] = {"steps": template_steps}
    policy_path.write_text(yaml.safe_dump(policy), encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "template_id": "perf",
        "slug": "perf",
        "current_step": template_steps[0],
        "meta": {},
        "steps": {
            sid: {"verified": False, "verified_at": None, "artifact_sha256": None}
            for sid in template_steps
        },
    }
    (repo_root / "manifests" / "work-unit.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")


def test_twenty_step_all_bounded(repo_root) -> None:
    _seed_twenty_step(repo_root)
    config = load_config(repo_root / ".overseer" / "config.yaml")
    start = time.monotonic()
    result = run_verify_step(
        config=config,
        repo_root=repo_root,
        options=VerifyStepOptions(verify_all=True),
    )
    elapsed = time.monotonic() - start
    assert result.exit_code == 0
    assert elapsed < 15.0

"""Stress tests for K7 bridge footprint resolution (§K7.8 stress tier)."""

from __future__ import annotations

import time
from pathlib import Path

from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST, MUSE_BRIDGE_WORKFLOW_DEST, resolve_footprint
from cli.kit_root import kit_root
from tests.support import FIXTURES, write_config


def test_large_workflow_with_many_policy_files_bounded(tmp_path: Path) -> None:
    kit = tmp_path / "kit"
    kit.mkdir()
    for sub in ("templates/scripts", "policy", "cursor/rules"):
        (kit / sub).mkdir(parents=True)
    (kit / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    for name in (
        "OVERSEER-HANDOVER.template.md",
        "ROADMAP.template.md",
        "STANDING-DECISIONS.template.md",
        "MUSE-BRIDGE-WORKFLOW.template.md",
    ):
        (kit / "templates" / name).write_text("# {{repo.name}}\n" + ("x\n" * 5000), encoding="utf-8")
    (kit / "templates" / "scripts" / "muse-bridge-deploy.sh.template").write_text(
        "#!/usr/bin/env bash\n# {{vcs.git.remote}}\n" + "echo line\n" * 200,
        encoding="utf-8",
    )
    for index in range(150):
        (kit / "policy" / f"p{index}.yaml").write_text(f"k: {index}\n", encoding="utf-8")
        (kit / "cursor" / "rules" / f"r{index}.mdc").write_text(f"rule {index}\n", encoding="utf-8")

    repo = tmp_path / "repo"
    repo.mkdir()
    from tests.support import write_config

    write_config(repo, "config-overseer-kit-dogfood.yaml")
    from adapters.config import load_config

    config = load_config(repo / ".overseer" / "config.yaml")

    start = time.perf_counter()
    files = resolve_footprint(config, kit=kit)
    elapsed = time.perf_counter() - start
    dests = {f.destination for f in files}
    assert MUSE_BRIDGE_WORKFLOW_DEST in dests
    assert MUSE_BRIDGE_DEPLOY_DEST in dests
    assert elapsed < 3.0
    assert len(files) >= 150

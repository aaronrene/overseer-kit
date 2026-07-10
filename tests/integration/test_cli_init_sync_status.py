"""Integration tests for init/sync/status across regimes."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from cli.footprint import resolve_footprint
from cli.kit_root import kit_root
from tests.support import (
    FIXTURES,
    git_status_runner,
    muse_mirror_status_runner,
    muse_status_runner,
    run_cli,
)


@pytest.mark.parametrize(
    ("fixture", "runner_factory"),
    [
        ("config-git-only.yaml", lambda p: git_status_runner()),
        ("config-muse-only.yaml", lambda p: muse_status_runner(p)),
        ("config-muse-git-mirror.yaml", lambda p: muse_mirror_status_runner(p)),
    ],
)
def test_init_full_footprint_per_regime(tmp_path: Path, fixture: str, runner_factory) -> None:
    code = run_cli(
        ["init", "--from-config", str(FIXTURES / fixture), "--non-interactive"],
        cwd=tmp_path,
        kit=kit_root(),
    )
    assert code == 0
    config = load_config(tmp_path / ".overseer" / "config.yaml")
    footprint = resolve_footprint(config, kit=kit_root())
    for item in footprint:
        assert (tmp_path / item.destination).is_file()

    sd = tmp_path / ".overseer" / "STANDING-DECISIONS.reference.md"
    assert sd.is_file()
    assert "SD-1" in sd.read_text(encoding="utf-8")

    if config.docs.coordination is None:
        coord = [
            f.destination
            for f in footprint
            if f.source.endswith("CROSS-REPO-COORDINATION.template.md")
        ]
        assert coord == []

    code = run_cli(
        ["status", "--json"],
        cwd=tmp_path,
        runner=runner_factory(tmp_path),
    )
    assert code == 0

    code = run_cli(["sync", "-y"], cwd=tmp_path, runner=runner_factory(tmp_path))
    assert code == 0


def test_destination_collision_fails_closed(tmp_path: Path) -> None:
    data = yaml.safe_load((FIXTURES / "config-git-only.yaml").read_text(encoding="utf-8"))
    data["docs"]["handover"] = "ROADMAP.md"
    data["docs"]["roadmap"] = "ROADMAP.md"
    cfg = tmp_path / "collision.yaml"
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    code = run_cli(
        ["init", "--from-config", str(cfg), "--non-interactive"],
        cwd=tmp_path,
        kit=kit_root(),
    )
    assert code == 2

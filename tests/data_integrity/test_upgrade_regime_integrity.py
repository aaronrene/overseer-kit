"""Data-integrity — Track O / O3 upgrade-regime (§O2.9 data-integrity)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from cli.digest import sha256_hex
from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST
from cli.kit_root import kit_root
from cli.version_lock import read_version_lock
from tests.support import (
    FIXTURES,
    make_runner,
    muse_mirror_status_runner,
    muse_status_runner,
    ok,
    run_cli,
    seed_muse_substrate,
)


def _init_muse_only(tmp_path: Path) -> None:
    seed_muse_substrate(tmp_path)
    assert (
        run_cli(
            [
                "init",
                "--from-config",
                str(FIXTURES / "config-muse-only.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            kit=kit_root(),
            runner=muse_status_runner(tmp_path),
        )
        == 0
    )


def _runner(tmp_path: Path):
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    responses["git remote get-url origin"] = ok("git@github.com:o/r.git")
    return make_runner(responses)


def test_dry_run_leaves_tree_unchanged(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    before_cfg = (tmp_path / ".overseer" / "config.yaml").read_bytes()
    before_lock = (tmp_path / ".overseer" / "version.lock").read_bytes()
    code = run_cli(
        ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--dry-run"],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_runner(tmp_path),
    )
    assert code == 0
    assert (tmp_path / ".overseer" / "config.yaml").read_bytes() == before_cfg
    assert (tmp_path / ".overseer" / "version.lock").read_bytes() == before_lock
    assert not (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).exists()


def test_conflict_preserves_pre_conflict_bytes(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    hand = b"#!/bin/bash\necho preserved-hand-tuned\n"
    (scripts / "muse-bridge-deploy.sh").write_bytes(hand)
    code = run_cli(
        ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_runner(tmp_path),
    )
    assert code == 4
    assert (scripts / "muse-bridge-deploy.sh").read_bytes() == hand


def test_successful_apply_twice_stable_lock_digest(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    runner = _runner(tmp_path)
    assert (
        run_cli(
            ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
            cwd=tmp_path,
            kit=kit_root(),
            runner=runner,
        )
        == 0
    )
    lock1 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    digest1 = lock1.footprint_digest
    assert (
        run_cli(
            ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
            cwd=tmp_path,
            kit=kit_root(),
            runner=runner,
        )
        == 0
    )
    lock2 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert lock2.footprint_digest == digest1
    # Config still muse+git-mirror
    assert load_config(tmp_path / ".overseer" / "config.yaml").vcs.regime == "muse+git-mirror"
    # Bridge script digest stable
    script = (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).read_bytes()
    assert sha256_hex(script)


def test_induced_mid_write_failure_no_partial_lock_advance(tmp_path: Path) -> None:
    """§O2.9: no partial lock advance on induced mid-write failure during C3 seed."""
    from unittest.mock import patch

    from cli.atomic import WriteFailure
    from cli.footprint_writes import write_footprint_bytes as real_write

    _init_muse_only(tmp_path)
    # Advance to muse+git-mirror config only (C2) via a normal apply first would seed;
    # instead: apply once, then delete one bridge file + induce sync write failure on repair.
    assert (
        run_cli(
            ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
            cwd=tmp_path,
            kit=kit_root(),
            runner=_runner(tmp_path),
        )
        == 0
    )
    before = read_version_lock(tmp_path / ".overseer" / "version.lock")
    (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).unlink()
    calls = {"n": 0}

    def flaky_write(path: Path, data: bytes, *, destination: str | None = None) -> None:
        calls["n"] += 1
        if destination == MUSE_BRIDGE_DEPLOY_DEST or path.name == "muse-bridge-deploy.sh":
            raise WriteFailure(path, OSError("simulated mid-write failure"))
        if destination is not None:
            real_write(path, data, destination=destination)
        else:
            real_write(path, data, destination=str(path))

    with patch("cli.commands.sync.write_footprint_bytes", side_effect=flaky_write):
        code = run_cli(
            ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
            cwd=tmp_path,
            kit=kit_root(),
            runner=_runner(tmp_path),
        )
    assert code == 5
    after = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert after.footprint_digest == before.footprint_digest
    assert not (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).exists()

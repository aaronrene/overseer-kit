"""Data-integrity tests for K7 bridge footprint (§K7.8 data-integrity tier)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from cli.digest import FootprintRecord, compute_footprint_digest, sha256_hex
from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST, MUSE_BRIDGE_WORKFLOW_DEST, resolve_footprint
from cli.kit_root import kit_root
from cli.version_lock import read_version_lock
from tests.support import FIXTURES, muse_mirror_status_runner, run_cli


def test_muse_mirror_init_twice_identical_digest(tmp_path: Path) -> None:
    runner = muse_mirror_status_runner(tmp_path)
    args = [
        "init",
        "--from-config",
        str(FIXTURES / "config-muse-git-mirror.yaml"),
        "--non-interactive",
    ]
    assert run_cli(args, cwd=tmp_path, kit=kit_root(), runner=runner) == 0
    lock1 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert run_cli(args, cwd=tmp_path, kit=kit_root(), runner=runner) == 0
    lock2 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert lock1.footprint_digest == lock2.footprint_digest


def test_kit_only_digest_includes_bridge_when_muse_mirror(tmp_path: Path) -> None:
    run_cli(
        [
            "init",
            "--from-config",
            str(FIXTURES / "config-muse-git-mirror.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=muse_mirror_status_runner(tmp_path),
    )
    from adapters.config import load_config

    config = load_config(tmp_path / ".overseer" / "config.yaml")
    rendered = resolve_footprint(config, kit=kit_root())
    records = [
        FootprintRecord(item.destination, sha256_hex((tmp_path / item.destination).read_bytes()))
        for item in rendered
    ]
    expected = compute_footprint_digest(records)
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert lock.footprint_digest == expected
    assert MUSE_BRIDGE_WORKFLOW_DEST in {e.path for e in lock.footprint}


def test_git_only_digest_omits_bridge_destinations(tmp_path: Path) -> None:
    run_cli(["init", "--regime", "git-only", "--non-interactive"], cwd=tmp_path, kit=kit_root())
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    paths = {e.path for e in lock.footprint}
    assert MUSE_BRIDGE_WORKFLOW_DEST not in paths
    assert MUSE_BRIDGE_DEPLOY_DEST not in paths


def test_bridge_write_failure_leaves_lock_unchanged(tmp_path: Path) -> None:
    run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
        kit=kit_root(),
    )
    before = read_version_lock(tmp_path / ".overseer" / "version.lock")
    mirror_cfg = (FIXTURES / "config-muse-git-mirror.yaml").read_text(encoding="utf-8")
    (tmp_path / ".overseer" / "config.yaml").write_text(mirror_cfg, encoding="utf-8")
    calls = {"n": 0}

    def flaky_write(path: Path, data: bytes, *, destination: str) -> None:
        calls["n"] += 1
        if MUSE_BRIDGE_DEPLOY_DEST in destination and calls["n"] >= 1:
            from cli.atomic import WriteFailure

            raise WriteFailure(path, OSError("simulated failure"))
        from cli.footprint_writes import write_footprint_bytes as real

        real(path, data, destination=destination)

    with patch("cli.commands.sync.write_footprint_bytes", side_effect=flaky_write):
        code = run_cli(
            ["sync", "-y"],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
        )
    assert code == 5
    after = read_version_lock(tmp_path / ".overseer" / "version.lock")
    assert after.footprint_digest == before.footprint_digest

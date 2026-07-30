"""Data-integrity — preserved shared lock sha + kit-only digest (§PSA.8)."""

from __future__ import annotations

from pathlib import Path

from cli.digest import sha256_hex
from cli.version_lock import ORIGIN_PRESERVED, compute_lock_digest, read_version_lock
from tests.support import PILOT, muse_mirror_status_runner, run_cli, seed_pilot_tree


def test_preserved_shared_lock_sha_matches_disk_and_digest(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    policy = tmp_path / ".overseer" / "policy"
    policy.mkdir(parents=True, exist_ok=True)
    hand = b"consumer-owned: true\n"
    (policy / "tiers.yaml").write_bytes(hand)

    args = [
        "init",
        "--migrate",
        "--force",
        "--preserve-shared-assets",
        "--from-config",
        str(PILOT / "config-scooling.yaml"),
        "--non-interactive",
    ]
    runner = muse_mirror_status_runner(tmp_path)
    assert run_cli(args, cwd=tmp_path, runner=runner) == 0
    lock1 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    entry1 = next(e for e in lock1.footprint if e.path == ".overseer/policy/tiers.yaml")
    assert entry1.origin == ORIGIN_PRESERVED
    assert entry1.sha256 == sha256_hex(hand)
    assert (policy / "tiers.yaml").read_bytes() == hand
    assert lock1.footprint_digest == compute_lock_digest(list(lock1.footprint))

    assert run_cli(args, cwd=tmp_path, runner=runner) == 0
    lock2 = read_version_lock(tmp_path / ".overseer" / "version.lock")
    entry2 = next(e for e in lock2.footprint if e.path == ".overseer/policy/tiers.yaml")
    assert entry2.origin == ORIGIN_PRESERVED
    assert entry2.sha256 == entry1.sha256
    assert (policy / "tiers.yaml").read_bytes() == hand
    assert lock2.footprint_digest == compute_lock_digest(list(lock2.footprint))

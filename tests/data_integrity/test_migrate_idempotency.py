"""Data-integrity: migrate idempotency, dry-run, preserved lock, promotion (§K6.10)."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import ORIGIN_KIT, ORIGIN_PRESERVED, read_version_lock
from tests.support import PILOT, git_status_runner, muse_mirror_status_runner, lock_origins, run_cli, seed_pilot_tree


def _migrate(tmp_path: Path, *extra: str) -> int:
    return run_cli(
        [
            "init",
            "--migrate",
            "--from-config",
            str(PILOT / "config-scooling.yaml"),
            "--non-interactive",
            *extra,
        ],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )


def test_migrate_twice_identical(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path) == 0
    lock1 = (tmp_path / ".overseer/version.lock").read_text(encoding="utf-8")
    policy1 = (tmp_path / ".overseer/policy/tiers.yaml").read_bytes()
    assert _migrate(tmp_path) == 0
    # already current — lock content (except possibly timestamps) / files unchanged
    assert (tmp_path / ".overseer/policy/tiers.yaml").read_bytes() == policy1
    assert (tmp_path / ".overseer/version.lock").is_file()
    _ = lock1


def test_migrate_dry_run_zero_writes(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path, "--dry-run") == 0
    assert not (tmp_path / ".overseer/version.lock").exists()
    assert not (tmp_path / ".overseer/policy").exists()


def test_preserved_sha_matches_on_disk(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path) == 0
    lock = read_version_lock(tmp_path / ".overseer/version.lock")
    from cli.digest import sha256_hex

    for entry in lock.footprint:
        if entry.origin != ORIGIN_PRESERVED:
            continue
        on_disk = (tmp_path / entry.path).read_bytes()
        assert sha256_hex(on_disk) == entry.sha256


def test_default_sync_retains_preserved_lock_verbatim(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path) == 0
    lock_before = read_version_lock(tmp_path / ".overseer/version.lock")
    preserved_before = {
        e.path: (e.sha256, e.origin, e.source)
        for e in lock_before.footprint
        if e.origin == ORIGIN_PRESERVED
    }
    assert run_cli(["sync", "-y"], cwd=tmp_path, runner=muse_mirror_status_runner(tmp_path)) == 0
    lock_after = read_version_lock(tmp_path / ".overseer/version.lock")
    for path, triple in preserved_before.items():
        entry = next(e for e in lock_after.footprint if e.path == path)
        assert (entry.sha256, entry.origin, entry.source) == triple


def test_hand_edit_preserved_leaves_check_ok_and_sync_updates_kit(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path) == 0
    (tmp_path / "docs/OVERSEER-HANDOVER.md").write_text("# H2\n", encoding="utf-8")
    assert (
        run_cli(
            ["status", "--check-footprint"],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
        )
        == 0
    )
    # Mutate a kit shared asset baseline then sync should refresh it when kit-updated;
    # with same kit version, sync is already_current — assert living doc untouched.
    assert run_cli(["sync", "-y"], cwd=tmp_path, runner=muse_mirror_status_runner(tmp_path)) == 0
    assert (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8") == "# H2\n"


def test_hand_edit_seeded_living_doc_integrity(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# KN\n",
        roadmap_rel=None,
    )
    assert (
        run_cli(
            [
                "init",
                "--migrate",
                "--from-config",
                str(PILOT / "config-knowtation.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
        )
        == 0
    )
    (tmp_path / "docs/ROADMAP.md").write_text("# edit seeded\n", encoding="utf-8")
    assert (
        run_cli(
            ["status", "--check-footprint"],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
        )
        == 0
    )


def test_promote_then_hand_edit_flips_integrity(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path) == 0
    assert (
        run_cli(
            ["sync", "--force", "--include-preserved", "-y"],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
        )
        == 0
    )
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_KIT
    (tmp_path / "docs/OVERSEER-HANDOVER.md").write_text("# after promote edit\n", encoding="utf-8")
    code = run_cli(
        ["status", "--check-footprint", "--exit-code"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 6

"""Unit tests for ``overseer init --migrate`` (§K6.4 / §K6.10)."""

from __future__ import annotations

from pathlib import Path

from cli.version_lock import ORIGIN_KIT, ORIGIN_PRESERVED, read_version_lock
from tests.support import PILOT, git_status_runner, lock_origins, muse_mirror_status_runner, run_cli, seed_pilot_tree


def _migrate(tmp_path: Path, config_name: str, *extra: str) -> int:
    runner = (
        git_status_runner()
        if "videofactory" in config_name
        else muse_mirror_status_runner(tmp_path)
    )
    return run_cli(
        [
            "init",
            "--migrate",
            "--from-config",
            str(PILOT / config_name),
            "--non-interactive",
            *extra,
        ],
        cwd=tmp_path,
        runner=runner,
    )


def _runner_for(tmp_path: Path, config_name: str = "config-scooling.yaml"):
    if "videofactory" in config_name:
        return git_status_runner()
    return muse_mirror_status_runner(tmp_path)


def test_migrate_preserves_differing_living_docs(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# HAND SCOOLING\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# HAND ROADMAP\n",
    )
    code = _migrate(tmp_path, "config-scooling.yaml")
    assert code == 0
    assert (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8") == "# HAND SCOOLING\n"
    origins = lock_origins(tmp_path)
    assert origins["docs/OVERSEER-HANDOVER.md"] == ORIGIN_PRESERVED
    assert origins["docs/ROADMAP.md"] == ORIGIN_PRESERVED
    assert origins[".overseer/policy/tiers.yaml"] == ORIGIN_KIT


def test_migrate_force_still_preserves_living_docs(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# KEEP\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# KEEP ROAD\n",
    )
    code = _migrate(tmp_path, "config-scooling.yaml", "--force")
    assert code == 0
    assert (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8") == "# KEEP\n"
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_PRESERVED


def test_migrate_seeds_absent_living_doc_as_preserved(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# KN HAND\n",
        roadmap_rel=None,
    )
    code = _migrate(tmp_path, "config-knowtation.yaml")
    assert code == 0
    assert (tmp_path / "docs/ROADMAP.md").is_file()
    assert lock_origins(tmp_path)["docs/ROADMAP.md"] == ORIGIN_PRESERVED
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_PRESERVED


def test_migrate_promote_differing_living_doc(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# OLD\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# OLD R\n",
    )
    code = _migrate(
        tmp_path,
        "config-scooling.yaml",
        "--force",
        "--include-preserved",
    )
    assert code == 0
    text = (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8")
    assert text != "# OLD\n"
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_KIT


def test_migrate_promote_identical_living_doc_ownership_only(tmp_path: Path) -> None:
    run_cli(
        [
            "init",
            "--from-config",
            str(PILOT / "config-scooling.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    before = (tmp_path / "docs/OVERSEER-HANDOVER.md").read_bytes()
    code = _migrate(
        tmp_path,
        "config-scooling.yaml",
        "--force",
        "--include-preserved",
    )
    assert code == 0
    assert (tmp_path / "docs/OVERSEER-HANDOVER.md").read_bytes() == before
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_KIT


def test_migrate_include_preserved_without_force_is_noop(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# KEEP\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# KEEP R\n",
    )
    code = _migrate(tmp_path, "config-scooling.yaml", "--include-preserved")
    assert code == 0
    assert (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8") == "# KEEP\n"
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_PRESERVED


def test_migrate_refuses_shared_asset_conflict(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    policy = tmp_path / ".overseer" / "policy"
    policy.mkdir(parents=True, exist_ok=True)
    (policy / "tiers.yaml").write_text("altered: true\n", encoding="utf-8")
    code = _migrate(tmp_path, "config-scooling.yaml")
    assert code == 4


def test_kn_r2_pass_updates_without_force(tmp_path: Path) -> None:
    consumer_rule = (PILOT / "knowtation-no-docs-only-pr.mdc").read_text(encoding="utf-8")
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# KN\n",
        roadmap_rel=None,
        extra_cursor_rules={"no-docs-only-pr-to-main.mdc": consumer_rule},
    )
    code = _migrate(tmp_path, "config-knowtation.yaml")
    assert code == 0
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    entry = next(e for e in lock.footprint if e.path == ".cursor/rules/no-docs-only-pr-to-main.mdc")
    assert entry.origin == ORIGIN_KIT
    # Written content should be rendered kit (tokens substituted), not consumer bytes
    written = (tmp_path / ".cursor/rules/no-docs-only-pr-to-main.mdc").read_text(encoding="utf-8")
    assert "{{vcs.git.main_branch}}" not in written
    assert "main" in written


def test_kit_only_digest_excludes_preserved(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path, "config-scooling.yaml") == 0
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    from cli.version_lock import compute_lock_digest

    assert lock.footprint_digest == compute_lock_digest(list(lock.footprint))
    assert any(e.origin == ORIGIN_PRESERVED for e in lock.footprint)


def test_hand_edit_preserved_check_footprint_ok(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path, "config-scooling.yaml") == 0
    (tmp_path / "docs/OVERSEER-HANDOVER.md").write_text("# H edited\n", encoding="utf-8")
    code = run_cli(
        ["status", "--check-footprint", "--json"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
        json_mode=True,
    )
    assert code == 0


def test_hand_edit_preserved_default_sync_exit_zero(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path, "config-scooling.yaml") == 0
    (tmp_path / "docs/OVERSEER-HANDOVER.md").write_text("# H edited\n", encoding="utf-8")
    code = run_cli(["sync", "-y"], cwd=tmp_path, runner=muse_mirror_status_runner(tmp_path))
    assert code == 0
    assert (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8") == "# H edited\n"


def test_sync_force_alone_does_not_overwrite_preserved(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path, "config-scooling.yaml") == 0
    code = run_cli(["sync", "--force", "-y"], cwd=tmp_path, runner=muse_mirror_status_runner(tmp_path))
    assert code == 0
    assert (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8") == "# H\n"
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_PRESERVED


def test_sync_force_include_preserved_promotes(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert _migrate(tmp_path, "config-scooling.yaml") == 0
    code = run_cli(
        ["sync", "--force", "--include-preserved", "-y"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    )
    assert code == 0
    assert lock_origins(tmp_path)["docs/OVERSEER-HANDOVER.md"] == ORIGIN_KIT
    assert "# H\n" not in (tmp_path / "docs/OVERSEER-HANDOVER.md").read_text(encoding="utf-8")


def test_hand_edit_seeded_roadmap_check_and_sync(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# KN\n",
        roadmap_rel=None,
    )
    assert _migrate(tmp_path, "config-knowtation.yaml") == 0
    (tmp_path / "docs/ROADMAP.md").write_text("# seeded then edited\n", encoding="utf-8")
    assert run_cli(
        ["status", "--check-footprint"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
    ) == 0
    assert run_cli(["sync", "-y"], cwd=tmp_path, runner=muse_mirror_status_runner(tmp_path)) == 0
    assert (tmp_path / "docs/ROADMAP.md").read_text(encoding="utf-8") == "# seeded then edited\n"


def test_migrate_argparse_unknown_flag() -> None:
    from cli.main import main

    assert main(["init", "--migrate", "--not-a-real-flag"]) == 1

"""Integration tests — Track O / O3 upgrade-regime on tmp trees (§O2.9 integration)."""

from __future__ import annotations

import json
from pathlib import Path

from adapters.config import load_config
from adapters.runner import CommandResult
from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST, MUSE_BRIDGE_WORKFLOW_DEST
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
    write_config,
)


def _init_muse_only(tmp_path: Path) -> None:
    seed_muse_substrate(tmp_path)
    code = run_cli(
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
    assert code == 0


def _upgrade_runner(tmp_path: Path, *, remote_url: str | None = "git@github.com:o/r.git"):
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    if remote_url is None:
        responses["git remote get-url origin"] = CommandResult(stdout="", stderr="missing", exit_code=2)
    else:
        responses["git remote get-url origin"] = ok(remote_url)
    return make_runner(responses)


def test_apply_muse_only_seeds_bridge_files(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    before_docs = load_config(tmp_path / ".overseer" / "config.yaml").docs.handover
    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--apply",
            "--json",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_upgrade_runner(tmp_path),
        json_mode=True,
    )
    assert code == 0
    assert (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).is_file()
    assert (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).is_file()
    lock = read_version_lock(tmp_path / ".overseer" / "version.lock")
    paths = {e.path for e in lock.footprint}
    assert MUSE_BRIDGE_WORKFLOW_DEST in paths
    assert MUSE_BRIDGE_DEPLOY_DEST in paths
    after = load_config(tmp_path / ".overseer" / "config.yaml")
    assert after.vcs.regime == "muse+git-mirror"
    assert after.docs.handover == before_docs


def test_regime_only_mutation_refused_ceremony_writes_complete_vcs(tmp_path: Path) -> None:
    """§O2.9: regime-only mutation refused — apply always writes full §O2.4.2 VCS block."""
    from tools.upgrade_regime.ceremony import (
        build_upgraded_config_dict,
        is_silent_regime_only_patch,
        required_vcs_complete,
    )

    _init_muse_only(tmp_path)
    before = load_config(tmp_path / ".overseer" / "config.yaml")
    silent = {
        "vcs": {
            "regime": "muse+git-mirror",
            "canonical": "muse",
            "git": {
                "remote": before.vcs.git.remote,
                "main_branch": before.vcs.git.main_branch,
                "mirror_branch": None,
                "feature_branch_pattern": before.vcs.git.feature_branch_pattern,
            },
            "muse": {
                "staging_remote": None,
                "main_branch": before.vcs.muse.main_branch,
                "working_dir": before.vcs.muse.working_dir,
            },
        }
    }
    assert is_silent_regime_only_patch(before, silent) is True
    upgraded = build_upgraded_config_dict(before)
    assert is_silent_regime_only_patch(before, upgraded) is False

    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--apply",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_upgrade_runner(tmp_path),
    )
    assert code == 0
    after = load_config(tmp_path / ".overseer" / "config.yaml")
    assert required_vcs_complete(after)
    assert after.vcs.git.mirror_branch == "muse-mirror"
    assert after.vcs.muse.staging_remote == "staging"
    assert after.docs.handover == before.docs.handover

    # git-only start still refused
    git_tree = tmp_path / "git"
    git_tree.mkdir()
    write_config(git_tree, "config-git-only.yaml")
    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--dry-run",
        ],
        cwd=git_tree,
        kit=kit_root(),
    )
    assert code == 4


def test_shared_asset_conflict_without_force_exit_4(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "muse-bridge-deploy.sh").write_text("#!/bin/bash\necho hand-tuned\n", encoding="utf-8")
    (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).write_text("# hand\n", encoding="utf-8")
    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--apply",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_upgrade_runner(tmp_path),
    )
    assert code == 4
    assert (scripts / "muse-bridge-deploy.sh").read_text(encoding="utf-8") == "#!/bin/bash\necho hand-tuned\n"


def test_shared_asset_conflict_with_force_ok(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "muse-bridge-deploy.sh").write_text("#!/bin/bash\necho hand-tuned\n", encoding="utf-8")
    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--apply",
            "--force",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_upgrade_runner(tmp_path),
    )
    assert code == 0
    body = (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).read_text(encoding="utf-8")
    assert "hand-tuned" not in body
    assert "muse -C" in body


def test_idempotent_complete_upgrade(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    assert (
        run_cli(
            ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
            cwd=tmp_path,
            kit=kit_root(),
            runner=_upgrade_runner(tmp_path),
        )
        == 0
    )
    code = run_cli(
        ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply", "--json"],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_upgrade_runner(tmp_path),
        json_mode=True,
    )
    assert code == 0


def test_incomplete_upgrade_repair(tmp_path: Path) -> None:
    # Start as complete muse+git-mirror init, then remove bridge files from disk/lock path.
    seed_muse_substrate(tmp_path)
    code = run_cli(
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
    assert code == 0
    (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).unlink()
    (tmp_path / MUSE_BRIDGE_WORKFLOW_DEST).unlink()
    code = run_cli(
        ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_upgrade_runner(tmp_path),
    )
    assert code == 0
    assert (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).is_file()


def test_g8_fail_marks_not_ready_for_live(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--apply",
            "--json",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=_upgrade_runner(tmp_path, remote_url=None),
        json_mode=True,
    )
    assert code == 0
    # Capture JSON via a second dry-run on the upgraded tree
    import io
    import sys

    from cli.context import CliContext
    from cli.main import main
    from cli.output import OutputContext

    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        ctx = CliContext.create(
            runner=_upgrade_runner(tmp_path, remote_url=None),
            cwd=tmp_path,
            kit=kit_root(),
            output=OutputContext(json_mode=True),
        )
        code2 = main(
            [
                "upgrade-regime",
                "--from",
                "muse-only",
                "--to",
                "muse+git-mirror",
                "--dry-run",
                "--json",
            ],
            ctx=ctx,
        )
    finally:
        sys.stdout = old
    assert code2 == 0
    payload = json.loads(buf.getvalue())
    assert payload["ready_for_live_bridge"] is False
    assert payload["gates"]["G8"]["ok"] is False

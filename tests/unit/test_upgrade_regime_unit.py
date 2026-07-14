"""Unit tests — Track O / O3 upgrade-regime classifiers and gates (§O2.9 unit)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import load_config
from adapters.runner import CommandResult
from adapters.templating import render_template
from cli.config_gen import load_config_from_dict
from cli.kit_root import kit_root
from cli.main import build_parser
from tests.support import FIXTURES, make_runner, ok, write_config
from tools.upgrade_regime.ceremony import (
    StartState,
    build_upgraded_config_dict,
    check_g3_deploy_script,
    check_g4_deploy_script,
    check_g5_deploy_script,
    check_g6_deploy_script,
    check_g8_git_remote,
    classify_start_state,
    docs_preserved,
    is_silent_regime_only_patch,
    required_vcs_complete,
)


def _load_muse_only():
    return load_config(FIXTURES / "config-muse-only.yaml")


def test_argparse_frozen_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--dry-run",
            "--apply",
            "--live-bridge",
            "--force",
            "-y",
        ]
    )
    assert args.command == "upgrade-regime"
    assert args.from_regime == "muse-only"
    assert args.to_regime == "muse+git-mirror"
    assert args.dry_run is True
    assert args.apply is True
    assert args.live_bridge is True
    assert args.force is True
    assert args.yes is True


def test_argparse_rejects_unsupported_from_pair() -> None:
    parser = build_parser()
    try:
        parser.parse_args(["upgrade-regime", "--from", "git-only", "--to", "muse+git-mirror"])
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert exc.code == 2


def test_classify_muse_only(tmp_path: Path) -> None:
    write_config(tmp_path, "config-muse-only.yaml")
    state = classify_start_state(tmp_path, tmp_path / ".overseer" / "config.yaml")
    assert state == StartState.MUSE_ONLY


def test_classify_missing_config(tmp_path: Path) -> None:
    state = classify_start_state(tmp_path, tmp_path / ".overseer" / "config.yaml")
    assert state == StartState.MISSING_CONFIG


def test_classify_wrong_regime_git_only(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    state = classify_start_state(tmp_path, tmp_path / ".overseer" / "config.yaml")
    assert state == StartState.WRONG_REGIME


def test_classify_incomplete_upgrade_without_bridge(tmp_path: Path) -> None:
    write_config(tmp_path, "config-muse-git-mirror.yaml")
    state = classify_start_state(tmp_path, tmp_path / ".overseer" / "config.yaml")
    assert state == StartState.INCOMPLETE_UPGRADE


def test_classify_complete_upgrade(tmp_path: Path) -> None:
    from tests.support import muse_mirror_status_runner, run_cli, seed_muse_substrate
    from cli.kit_root import kit_root

    seed_muse_substrate(tmp_path)
    assert (
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
        == 0
    )
    state = classify_start_state(tmp_path, tmp_path / ".overseer" / "config.yaml")
    assert state == StartState.COMPLETE_UPGRADE


def test_required_vcs_complete_and_build_preserves_docs() -> None:
    before = _load_muse_only()
    assert not required_vcs_complete(before)
    data = build_upgraded_config_dict(before)
    after = load_config_from_dict(data, "proj.yaml")
    assert required_vcs_complete(after)
    assert docs_preserved(before, after)
    assert after.docs.handover == before.docs.handover
    assert after.docs.roadmap == before.docs.roadmap
    assert after.vcs.git.mirror_branch == "muse-mirror"
    assert after.vcs.muse.staging_remote == "staging"


def test_silent_regime_only_patch_detector() -> None:
    before = _load_muse_only()
    silent = {
        "vcs": {
            "regime": "muse+git-mirror",
            "canonical": "muse",
            "git": {"remote": "origin", "main_branch": "main", "mirror_branch": None},
            "muse": {"staging_remote": None, "main_branch": "main"},
        }
    }
    assert is_silent_regime_only_patch(before, silent) is True
    good = build_upgraded_config_dict(before)
    assert is_silent_regime_only_patch(before, good) is False


def test_g3_g6_helpers_on_fixture_script() -> None:
    config = load_config(FIXTURES / "config-muse-git-mirror.yaml")
    script = render_template(
        kit_root() / "templates" / "scripts" / "muse-bridge-deploy.sh.template",
        config,
    )
    assert check_g3_deploy_script(script).ok
    assert check_g4_deploy_script(script).ok
    assert check_g5_deploy_script(script).ok
    assert check_g6_deploy_script(script).ok

    bad_push = script.replace(
        'push "${GIT_REMOTE}" "${MIRROR_BRANCH}"',
        "git push origin main",
    )
    assert not check_g4_deploy_script(bad_push).ok

    home = script + "\n# /Users/operator/secret\n"
    assert not check_g6_deploy_script(home).ok


def test_g8_remote_helper() -> None:
    runner = make_runner({"git remote get-url origin": ok("git@github.com:owner/repo.git")})
    assert check_g8_git_remote(Path("/tmp"), "origin", runner).ok

    runner_empty = make_runner(
        {"git remote get-url origin": CommandResult(stdout="", stderr="", exit_code=0)}
    )
    assert not check_g8_git_remote(Path("/tmp"), "origin", runner_empty).ok

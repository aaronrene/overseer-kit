"""Security tests for K7 bridge footprint (§K7.8 security tier)."""

from __future__ import annotations

import re
from pathlib import Path

from adapters.templating import render_template
from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST
from cli.kit_root import kit_root
from tests.support import FIXTURES, git_status_runner, muse_mirror_status_runner, ok, run_cli


def test_git_only_init_sync_never_invokes_muse(tmp_path: Path) -> None:
    runner = git_status_runner()
    runner.responses.update(
        {
            "git rev-parse origin/main": ok("c" * 40),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
        }
    )
    assert run_cli(
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
        runner=runner,
    ) == 0
    assert run_cli(["sync", "-y"], cwd=tmp_path, runner=runner) == 0
    assert run_cli(["status"], cwd=tmp_path, runner=runner) == 0
    assert run_cli(
        ["governance-sync", "--dry-run"],
        cwd=tmp_path,
        runner=runner,
    ) == 0
    assert not (tmp_path / "MUSE-BRIDGE-WORKFLOW.md").exists()
    assert all(not call[0].startswith("muse ") for call in runner.calls)


def test_muse_only_still_forbids_git_mirror_push(muse_only_config, repo_root) -> None:
    from tests.support import adapter_for, make_runner

    runner = make_runner({})
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.mirror(dry_run=False)
    assert result.pushed is False
    assert all("git push" not in call[0] for call in runner.calls)


def test_rendered_templates_contain_no_secrets_or_home_paths(muse_git_mirror_config) -> None:
    templates_dir = kit_root() / "templates"
    for name in (
        "MUSE-BRIDGE-WORKFLOW.template.md",
        "scripts/muse-bridge-deploy.sh.template",
    ):
        rendered = render_template(templates_dir / name, muse_git_mirror_config)
        assert "/Users/" not in rendered
        assert "AKIA" not in rendered
        assert "sha256:" not in rendered
        assert "password" not in rendered.lower()


def test_deploy_script_tokens_double_quoted_after_render(muse_git_mirror_config) -> None:
    script = render_template(
        kit_root() / "templates" / "scripts" / "muse-bridge-deploy.sh.template",
        muse_git_mirror_config,
    )
    # Remote/branch vars must be assigned from double-quoted literals (S11).
    assert 'GIT_REMOTE="origin"' in script or 'GIT_REMOTE="{{vcs.git.remote}}"' not in script
    assert re.search(r'MIRROR_BRANCH="[^"]+"', script)
    assert re.search(r'MAIN_BRANCH="[^"]+"', script)


def test_bridge_script_destination_confined_under_install_root(tmp_path: Path) -> None:
    assert (
        run_cli(
            [
                "init",
                "--from-config",
                str(FIXTURES / "config-muse-git-mirror.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
        )
        == 0
    )
    script = tmp_path / MUSE_BRIDGE_DEPLOY_DEST
    assert script.is_file()
    assert script.resolve().is_relative_to(tmp_path.resolve())


def test_no_live_git_export_in_k7_tests(tmp_path: Path) -> None:
    runner = muse_mirror_status_runner(tmp_path)
    run_cli(
        [
            "init",
            "--from-config",
            str(FIXTURES / "config-overseer-kit-dogfood.yaml"),
            "--non-interactive",
        ],
        cwd=tmp_path,
        runner=runner,
    )
    export_calls = [c for c in runner.calls if "git-export" in c[0]]
    assert export_calls == []

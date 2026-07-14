"""Security — Track O / O3 upgrade-regime fail-closed (§O2.9 security)."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from adapters.templating import render_template
from adapters.config import load_config
from cli.context import CliContext
from cli.kit_root import kit_root
from cli.main import main
from cli.output import OutputContext
from tests.support import (
    FIXTURES,
    make_runner,
    muse_mirror_status_runner,
    muse_status_runner,
    ok,
    run_cli,
    seed_muse_substrate,
)
from tools.upgrade_regime.ceremony import (
    check_g3_deploy_script,
    check_g4_deploy_script,
)


def test_no_secrets_in_ceremony_json(tmp_path: Path) -> None:
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
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    responses["git remote get-url origin"] = ok("git@github.com:o/r.git")
    buf = StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        ctx = CliContext.create(
            runner=make_runner(responses),
            cwd=tmp_path,
            kit=kit_root(),
            output=OutputContext(json_mode=True),
        )
        code = main(
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
    assert code == 0
    out = buf.getvalue()
    assert "AKIA" not in out
    assert "BEGIN PRIVATE KEY" not in out
    assert "/Users/" not in out
    payload = json.loads(out)
    assert "gates" in payload


def test_g3_g4_refuse_git_dir_dot_and_push_main() -> None:
    config = load_config(FIXTURES / "config-muse-git-mirror.yaml")
    script = render_template(
        kit_root() / "templates" / "scripts" / "muse-bridge-deploy.sh.template",
        config,
    )
    assert check_g3_deploy_script(script).ok
    assert check_g4_deploy_script(script).ok
    bad = '#!/bin/bash\nmuse bridge git-export --git-dir .\ngit push origin main\n'
    assert not check_g3_deploy_script(bad).ok
    assert not check_g4_deploy_script(bad).ok


def test_path_escape_config_refused(tmp_path: Path) -> None:
    seed_muse_substrate(tmp_path)
    outside = tmp_path / ".." / "outside-config.yaml"
    # Prefer absolute path outside repo
    outside = tmp_path.parent / f"escape-config-{tmp_path.name}.yaml"
    outside.write_text("overseer_config_version: 1\n", encoding="utf-8")
    try:
        code = run_cli(
            [
                "--config",
                str(outside),
                "upgrade-regime",
                "--from",
                "muse-only",
                "--to",
                "muse+git-mirror",
                "--dry-run",
            ],
            cwd=tmp_path,
            kit=kit_root(),
        )
        assert code == 4
    finally:
        outside.unlink(missing_ok=True)


def test_live_bridge_without_yes_refused(tmp_path: Path) -> None:
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
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    responses["git remote get-url origin"] = ok("git@github.com:o/r.git")
    # Apply first so gates can pass, then live without -y
    assert (
        run_cli(
            ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
            cwd=tmp_path,
            kit=kit_root(),
            runner=make_runner(responses),
        )
        == 0
    )
    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--apply",
            "--live-bridge",
        ],
        cwd=tmp_path,
        kit=kit_root(),
        runner=make_runner(responses),
    )
    assert code == 4


def test_git_only_baseline_unchanged_by_ceremony(tmp_path: Path) -> None:
    """K7 MuseHub-optional: git-only trees are refused, not rewritten."""
    assert (
        run_cli(
            ["init", "--regime", "git-only", "--non-interactive"],
            cwd=tmp_path,
            kit=kit_root(),
        )
        == 0
    )
    before = (tmp_path / ".overseer" / "config.yaml").read_bytes()
    code = run_cli(
        ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--apply"],
        cwd=tmp_path,
        kit=kit_root(),
    )
    assert code == 4
    assert (tmp_path / ".overseer" / "config.yaml").read_bytes() == before


def test_no_network_required_for_c0_c5(tmp_path: Path) -> None:
    """RecordingRunner only — no SubprocessRunner network for dry-run path."""
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
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    responses["git remote get-url origin"] = ok("git@github.com:o/r.git")
    runner = make_runner(responses)
    code = run_cli(
        ["upgrade-regime", "--from", "muse-only", "--to", "muse+git-mirror", "--dry-run"],
        cwd=tmp_path,
        kit=kit_root(),
        runner=runner,
    )
    assert code == 0
    # Only local git remote get-url (mocked) — no curl/gh/muse export
    for cmd, _cwd in runner.calls:
        assert "curl" not in cmd
        assert "gh " not in cmd
        assert "bridge git-export" not in cmd

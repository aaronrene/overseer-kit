"""Unit tests for K7 muse+git-mirror footprint (§K7.8 unit tier)."""

from __future__ import annotations

import re
import stat
from pathlib import Path

import pytest

from adapters.config import load_config
from adapters.errors import ConfigError
from adapters.templating import ALLOWED_TOKENS, render_template
from cli.footprint import (
    EXECUTABLE_FOOTPRINT_DESTINATIONS,
    MUSE_BRIDGE_DEPLOY_DEST,
    MUSE_BRIDGE_WORKFLOW_DEST,
    resolve_footprint,
)
from cli.footprint_writes import FOOTPRINT_EXECUTABLE_MODE, write_footprint_bytes
from cli.kit_root import kit_root
from tests.support import FIXTURES


def test_muse_git_mirror_footprint_includes_bridge_assets(muse_git_mirror_config) -> None:
    dests = {f.destination for f in resolve_footprint(muse_git_mirror_config)}
    assert MUSE_BRIDGE_WORKFLOW_DEST in dests
    assert MUSE_BRIDGE_DEPLOY_DEST in dests


def test_git_only_footprint_omits_bridge_assets(git_only_config) -> None:
    dests = {f.destination for f in resolve_footprint(git_only_config)}
    assert MUSE_BRIDGE_WORKFLOW_DEST not in dests
    assert MUSE_BRIDGE_DEPLOY_DEST not in dests


def test_muse_only_footprint_omits_bridge_assets(muse_only_config) -> None:
    dests = {f.destination for f in resolve_footprint(muse_only_config)}
    assert MUSE_BRIDGE_WORKFLOW_DEST not in dests
    assert MUSE_BRIDGE_DEPLOY_DEST not in dests


def test_overseer_kit_dogfood_config_matrix_loads() -> None:
    config = load_config(FIXTURES / "config-overseer-kit-dogfood.yaml")
    assert config.vcs.regime == "muse+git-mirror"
    assert config.vcs.canonical == "muse"
    assert config.vcs.git.mirror_branch == "muse-mirror"
    assert config.docs.coordination is None
    assert config.vcs.muse.working_dir is None
    dests = {f.destination for f in resolve_footprint(config)}
    assert MUSE_BRIDGE_WORKFLOW_DEST in dests


def test_bridge_templates_use_only_allowed_tokens(muse_git_mirror_config) -> None:
    templates_dir = kit_root() / "templates"
    for name in (
        "MUSE-BRIDGE-WORKFLOW.template.md",
        "scripts/muse-bridge-deploy.sh.template",
    ):
        raw = (templates_dir / name).read_text(encoding="utf-8")
        found = set(re.findall(r"\{\{([a-z][a-z0-9_.]*)\}\}", raw))
        assert found.issubset(ALLOWED_TOKENS), f"unexpected tokens in {name}: {found - ALLOWED_TOKENS}"
        rendered = render_template(templates_dir / name, muse_git_mirror_config)
        assert "{{" not in rendered


def test_rendered_deploy_script_safety_invariants(muse_git_mirror_config) -> None:
    script = render_template(
        kit_root() / "templates" / "scripts" / "muse-bridge-deploy.sh.template",
        muse_git_mirror_config,
    )
    assert "set -euo pipefail" in script
    assert "mirror directory equals repo root" in script
    assert "muse-bridge-sentinel" in script
    assert 'muse -C "${MUSE_ROOT}" bridge git-export' in script
    assert '--git-dir "${MIRROR_ABS}"' in script
    assert "origin" in script
    assert "muse-mirror" in script
    assert "main" in script
    assert 'push "${GIT_REMOTE}" "${MIRROR_BRANCH}"' in script
    assert "GIT_REMOTE_URL=" in script
    assert '--commit-message "${COMMIT_MSG}"' in script
    assert "--message " not in script
    assert "--no-push" not in script
    assert 'git push origin main' not in script
    assert 'push "${GIT_REMOTE}" "${MAIN_BRANCH}"' not in script
    for token in (
        "{{vcs.git.remote}}",
        "{{vcs.git.mirror_branch}}",
        "{{vcs.git.main_branch}}",
    ):
        assert token not in script


def test_rendered_workflow_hard_rules(muse_git_mirror_config) -> None:
    doc = render_template(
        kit_root() / "templates" / "MUSE-BRIDGE-WORKFLOW.template.md",
        muse_git_mirror_config,
    )
    assert "muse bridge git-export --git-dir ." in doc
    assert "git push origin main" in doc
    assert "muse-mirror" in doc
    assert "./scripts/muse-bridge-deploy.sh" in doc


def test_unknown_token_in_bridge_template_fails_closed(muse_git_mirror_config, tmp_path: Path) -> None:
    bad = tmp_path / "bad.template.md"
    bad.write_text("{{evil.token}}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown or unmapped template token"):
        render_template(bad, muse_git_mirror_config)


def test_write_footprint_bytes_sets_executable_on_deploy_script(tmp_path: Path) -> None:
    dest = MUSE_BRIDGE_DEPLOY_DEST
    assert dest in EXECUTABLE_FOOTPRINT_DESTINATIONS
    path = tmp_path / dest
    write_footprint_bytes(path, b"#!/usr/bin/env bash\necho ok\n", destination=dest)
    mode = path.stat().st_mode
    assert stat.S_IMODE(mode) == FOOTPRINT_EXECUTABLE_MODE

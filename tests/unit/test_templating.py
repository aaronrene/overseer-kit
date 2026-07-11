"""Unit tests for template token substitution."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.errors import ConfigError
from adapters.templating import (
    ALLOWED_TOKENS,
    build_token_map,
    render_template,
    substitute_tokens,
)
from tests.support import load_fixture_config


def test_build_token_map_git_only(git_only_config) -> None:
    token_map = build_token_map(git_only_config)
    assert token_map["repo.name"] == "test-git"
    assert token_map["docs.handover_path"] == "docs/OVERSEER-HANDOVER.md"
    assert token_map["vcs.regime"] == "git-only"
    assert token_map["docs.coordination"] == ""
    assert token_map["vcs.muse.staging_remote"] == ""


def test_build_token_map_muse_git_mirror(muse_git_mirror_config) -> None:
    token_map = build_token_map(muse_git_mirror_config)
    assert token_map["repo.name"] == "test-mirror"
    assert token_map["vcs.git.mirror_branch"] == "muse-mirror"
    assert token_map["docs.coordination_path"] == "docs/CROSS-REPO-COORDINATION.md"


def test_substitute_tokens_replaces_known_keys(git_only_config) -> None:
    token_map = build_token_map(git_only_config)
    text = "Repo {{repo.name}} uses {{vcs.regime}}; handover at {{docs.handover_path}}."
    result = substitute_tokens(text, token_map)
    assert "{{" not in result
    assert "test-git" in result
    assert "git-only" in result
    assert "docs/OVERSEER-HANDOVER.md" in result


def test_substitute_tokens_fail_closed_on_unknown() -> None:
    with pytest.raises(ConfigError, match="unknown or unmapped template token"):
        substitute_tokens("Hello {{evil.token}}", {}, fail_on_unknown=True)


def test_allowed_tokens_registry_matches_builder_keys(git_only_config) -> None:
    token_map = build_token_map(git_only_config)
    assert set(token_map) == ALLOWED_TOKENS


def test_render_handover_template(git_only_config, repo_root: Path) -> None:
    template = (
        Path(__file__).resolve().parents[2] / "templates" / "OVERSEER-HANDOVER.template.md"
    )
    rendered = render_template(template, git_only_config)
    assert "test-git" in rendered
    assert "{{repo.name}}" not in rendered
    assert "docs/OVERSEER-HANDOVER.md" in rendered


def test_render_all_templates_without_unknown_tokens(
    git_only_config,
    muse_only_config,
    muse_git_mirror_config,
) -> None:
    templates_dir = Path(__file__).resolve().parents[2] / "templates"
    base_templates = (
        "OVERSEER-HANDOVER.template.md",
        "ROADMAP.template.md",
        "STANDING-DECISIONS.template.md",
        "CROSS-REPO-COORDINATION.template.md",
    )
    bridge_templates = (
        "MUSE-BRIDGE-WORKFLOW.template.md",
        "scripts/muse-bridge-deploy.sh.template",
    )
    for config in (git_only_config, muse_only_config):
        for name in base_templates:
            rendered = render_template(templates_dir / name, config)
            assert "{{" not in rendered, f"unsubstituted token in {name} for {config.repo.name}"
    for name in base_templates + bridge_templates:
        rendered = render_template(templates_dir / name, muse_git_mirror_config)
        assert "{{" not in rendered, f"unsubstituted token in {name} for muse+git-mirror"


def test_render_template_missing_file_raises(git_only_config, tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="template file missing"):
        render_template(tmp_path / "missing.template.md", git_only_config)

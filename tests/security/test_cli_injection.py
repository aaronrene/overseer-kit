"""Security tests for CLI path traversal and injection."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.errors import ConfigError
from adapters.templating import substitute_tokens
from cli.paths import PathEscapeError, confine_path
from tests.support import run_cli


def test_confine_path_rejects_escape(tmp_path: Path) -> None:
    with pytest.raises(PathEscapeError):
        confine_path(tmp_path, "../outside")


def test_unknown_template_token_fails_closed() -> None:
    with pytest.raises(ConfigError):
        substitute_tokens("{{evil.token}}", {"repo.name": "x"}, fail_on_unknown=True)


def test_init_outside_repo_config_refused(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    code = run_cli(
        [
            "init",
            "--regime",
            "git-only",
            "--non-interactive",
            "--config",
            "../outside/config.yaml",
        ],
        cwd=repo,
    )
    assert code == 4

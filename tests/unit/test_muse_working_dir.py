"""Unit tests for ``vcs.muse.working_dir`` (§K6.5.1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.config import load_config
from adapters.errors import ConfigError
from adapters.factory import create_adapter
from cli.docs_paths import validate_muse_working_dir
from tests.support import PILOT, make_runner, ok


def test_working_dir_escape_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        validate_muse_working_dir(tmp_path, "../outside")


def test_working_dir_absolute_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        validate_muse_working_dir(tmp_path, "/tmp/elsewhere")


def test_working_dir_config_parse_rejects_dotdot(tmp_path: Path) -> None:
    text = (PILOT / "config-musehub.yaml").read_text(encoding="utf-8")
    text = text.replace("working_dir: musehub", "working_dir: ../escape")
    cfg = tmp_path / "bad.yaml"
    cfg.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(cfg)


def test_musehub_adapter_uses_working_dir(tmp_path: Path) -> None:
    (tmp_path / "musehub").mkdir()
    config = load_config(PILOT / "config-musehub.yaml")
    muse_cwd = (tmp_path / "musehub").resolve()
    runner = make_runner(
        {
            f"muse -C {muse_cwd} branch --show-current": ok("main"),
            f"muse -C {muse_cwd} status --porcelain": ok(""),
        }
    )
    adapter = create_adapter(config, tmp_path, runner=runner)
    result = adapter.status()
    assert not isinstance(result, Exception)
    assert result.branch == "main"
    assert any("musehub" in command for command, _cwd in runner.calls)

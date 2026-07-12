"""Integration: status surfaces hollow Muse substrate."""

from __future__ import annotations

import json
import shutil
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from cli.context import CliContext
from cli.main import main
from cli.output import OutputContext
from tests.support import FIXTURES, make_runner, ok


def _seed_muse_mirror_repo(tmp_path: Path) -> None:
    overseer = tmp_path / ".overseer"
    overseer.mkdir()
    shutil.copy(FIXTURES / "config-muse-git-mirror.yaml", overseer / "config.yaml")
    (overseer / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:0\ninstalled_at: '2026-01-01'\n"
        "synced_at: '2026-01-01'\nfootprint: []\n",
        encoding="utf-8",
    )
    (tmp_path / ".muse").mkdir()


def test_status_exit_code_on_hollow_muse_substrate(tmp_path: Path) -> None:
    _seed_muse_mirror_repo(tmp_path)
    root = str(tmp_path)
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("main"),
            f"muse -C {root} status --json": ok('{"dirty": true}'),
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
        }
    )
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["status", "--json", "--exit-code"],
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=runner,
                output=OutputContext(json_mode=True),
            ),
        )
    assert code == 2
    payload = json.loads(out.getvalue())
    assert payload["substrate"]["state"] == "hollow"
    assert payload["substrate"]["ok"] is False
    assert "muse init --force" in (payload["substrate"]["remediation"] or "")

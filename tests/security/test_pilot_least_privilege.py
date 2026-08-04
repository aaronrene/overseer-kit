"""Security: pilot least-privilege and no secret leak (§K6.9 / §K6.10)."""

from __future__ import annotations

import re
from pathlib import Path

from adapters.config import load_config
from adapters.errors import ConfigError
from adapters.factory import create_adapter
from cli.docs_paths import validate_muse_working_dir
from tests.support import PILOT, make_runner, ok, run_cli, seed_pilot_tree


def test_muse_only_zero_git_calls(tmp_path: Path) -> None:
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
    adapter.status()
    adapter.mirror(dry_run=True)
    head = adapter.read_head("origin/main")
    assert "git forbidden" in str(head).lower() or "forbidden" in str(head).lower()
    assert not any(command.startswith("git ") for command, _cwd in runner.calls)


def test_working_dir_escape_exit_two(tmp_path: Path) -> None:
    try:
        validate_muse_working_dir(tmp_path, "../../etc")
        raised = False
    except ConfigError:
        raised = True
    assert raised


def test_migrate_outputs_free_of_secrets_and_abs_paths(tmp_path: Path, capsys) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    code = run_cli(
        [
            "init",
            "--migrate",
            "--from-config",
            str(PILOT / "config-scooling.yaml"),
            "--non-interactive",
            "--json",
        ],
        cwd=tmp_path,
        json_mode=True,
    )
    assert code == 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "AKIA" not in combined
    assert "token=" not in combined.lower()
    # Absolute machine paths banned in CLI streams
    assert str(tmp_path.resolve()) not in combined


def test_include_preserved_absent_from_default_pilot_docs() -> None:
    runbook = Path("docs/archive/operators/K6-PILOT-OPERATOR-RUNBOOK.md").read_text(encoding="utf-8")
    assert "--force --include-preserved" in runbook
    assert "Never" in runbook or "never" in runbook
    assert "pilot-forbidden" in runbook.lower() or "never" in runbook.lower()
    # Default sync examples must not recommend the combo
    assert re.search(r"Never.*--force --include-preserved", runbook, re.I | re.S)

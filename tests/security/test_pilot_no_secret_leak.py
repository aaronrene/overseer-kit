"""Security: pilot migrate/sync reports contain no secret leakage (§K6.10)."""

from __future__ import annotations

from pathlib import Path

from tests.support import PILOT, git_status_runner, muse_mirror_status_runner, run_cli, seed_pilot_tree


SECRETISH = (
    "sk-live-",
    "ghp_",
    "xoxb-",
    "BEGIN PRIVATE KEY",
    "password=",
)


def test_pilot_no_secret_leak_in_lock_or_status(tmp_path: Path, capsys) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    assert (
        run_cli(
            [
                "init",
                "--migrate",
                "--from-config",
                str(PILOT / "config-scooling.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            runner=muse_mirror_status_runner(tmp_path),
        )
        == 0
    )
    lock_text = (tmp_path / ".overseer/version.lock").read_text(encoding="utf-8")
    for needle in SECRETISH:
        assert needle not in lock_text
    run_cli(
        ["status", "--check-footprint", "--json"],
        cwd=tmp_path,
        runner=muse_mirror_status_runner(tmp_path),
        json_mode=True,
    )
    out = capsys.readouterr().out + capsys.readouterr().err
    for needle in SECRETISH:
        assert needle not in out
    assert "/Users/" not in out

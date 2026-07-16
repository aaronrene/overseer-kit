"""Stress tests for Track Q / Q3 Tauri desktop packaging."""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.app import seed_app_repo
from tests.fixtures.desktop import make_desktop_launcher
from tools.desktop.banner import parse_startup_stderr


def test_repeated_launch_stop_cycles_leave_no_tmp_artifacts(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    for cycle in range(5):
        launcher = make_desktop_launcher(tmp_path, seed=False)
        banner = launcher.start()
        assert parse_startup_stderr(
            [
                "ok app listening\n",
                f"url: {banner.url}\n",
                f"session_credential: {banner.session_credential}\n",
                f"csrf_token: {banner.csrf_token}\n",
            ]
        )
        launcher.stop()

    temps = list(tmp_path.rglob("*.overseer.tmp"))
    assert temps == []

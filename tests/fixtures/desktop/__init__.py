"""Fixture helpers for Track Q / Q3 desktop packaging tests."""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.app import free_port, seed_app_repo
from tests.support import KIT_ROOT
from tools.desktop.launcher import DesktopLauncher, resolve_kit_root, resolve_repo_root


def make_desktop_launcher(
    tmp_path: Path,
    *,
    port: int | None = None,
    seed: bool = True,
) -> DesktopLauncher:
    """Seed a repo and return a launcher bound to an ephemeral port."""
    if seed:
        seed_app_repo(tmp_path)
    chosen = port or free_port()
    kit = resolve_kit_root(KIT_ROOT)
    repo = resolve_repo_root(kit=kit, explicit=tmp_path)
    return DesktopLauncher(kit_root_path=kit, repo_root=repo, port=chosen)

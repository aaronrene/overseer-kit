"""Data-integrity tests for Track Q / Q3 Tauri desktop packaging."""

from __future__ import annotations

import subprocess
from pathlib import Path

from tests.fixtures.app import seed_app_repo
from tests.fixtures.desktop import make_desktop_launcher
from tests.support import KIT_ROOT
from tools.desktop.launcher import build_launch_argv
from tools.desktop.manifest import DesktopManifest, validate_desktop_manifest


def test_launch_stop_twice_yields_same_health_shape(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    first = make_desktop_launcher(tmp_path, seed=False)
    second = make_desktop_launcher(tmp_path, seed=False)
    try:
        banner_one = first.start()
        banner_two = second.start()
        assert banner_one.url.startswith("http://127.0.0.1:")
        assert banner_two.url.startswith("http://127.0.0.1:")
        assert banner_one.session_credential != banner_two.session_credential
        assert banner_one.csrf_token != banner_two.csrf_token
    finally:
        first.stop()
        second.stop()


def test_bundle_script_produces_complete_kit_tree(tmp_path: Path) -> None:
    dest = KIT_ROOT / "desktop" / "src-tauri" / "resources" / "kit"
    if dest.exists():
        import shutil

        shutil.rmtree(dest)

    subprocess.run(
        [str(KIT_ROOT / "scripts" / "bundle-desktop-kit.sh")],
        cwd=KIT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    for rel in (
        "cli/ok",
        "adapters/__init__.py",
        "tools/app/server.py",
        "VERSION",
    ):
        assert (dest / rel).is_file(), rel

    argv = build_launch_argv(kit_root_path=dest, repo_root=tmp_path, port=9876)
    assert argv[0].endswith("/cli/ok")
    assert "9876" in argv


def test_manifest_still_valid_after_bundle(tmp_path: Path) -> None:
    manifest = DesktopManifest.from_kit_root(KIT_ROOT)
    assert validate_desktop_manifest(manifest) == []

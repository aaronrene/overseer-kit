"""Performance tests for Track Q / Q3 Tauri desktop packaging."""

from __future__ import annotations

import time
from pathlib import Path

from tests.fixtures.desktop import make_desktop_launcher
from tests.support import KIT_ROOT
from tools.desktop.manifest import DesktopManifest, validate_desktop_manifest


def test_desktop_launcher_startup_within_budget(tmp_path: Path) -> None:
    launcher = make_desktop_launcher(tmp_path)
    try:
        start = time.monotonic()
        launcher.start()
        elapsed = time.monotonic() - start
        assert elapsed < 5.0
    finally:
        launcher.stop()


def test_manifest_validation_is_bounded(tmp_path: Path) -> None:
    manifest = DesktopManifest.from_kit_root(KIT_ROOT)
    start = time.monotonic()
    for _ in range(20):
        validate_desktop_manifest(manifest)
    elapsed = time.monotonic() - start
    assert elapsed < 1.0

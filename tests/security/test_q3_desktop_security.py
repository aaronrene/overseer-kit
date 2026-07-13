"""Security tests for Track Q / Q3 Tauri desktop packaging."""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.desktop import make_desktop_launcher
from tests.support import KIT_ROOT
from tools.desktop.init_script import build_auth_bootstrap_script
from tools.desktop.launcher import build_launch_argv
from tools.desktop.manifest import DesktopManifest, validate_desktop_manifest


def test_launch_argv_rejects_shell_metacharacters_in_paths(tmp_path: Path) -> None:
    weird = tmp_path / "weird;rm -rf"
    weird.mkdir()
    argv = build_launch_argv(kit_root_path=KIT_ROOT, repo_root=weird, port=8765)
    joined = " ".join(argv)
    assert ";rm" in joined
    assert "eval" not in joined
    assert argv[0].endswith("/cli/ok")


def test_init_script_does_not_persist_credentials() -> None:
    script = build_auth_bootstrap_script(session_credential="secret", csrf_token="csrf")
    assert "localStorage" not in script
    assert "sessionStorage" not in script
    assert "document.cookie" not in script


def test_desktop_launcher_does_not_write_secrets_to_repo(tmp_path: Path) -> None:
    launcher = make_desktop_launcher(tmp_path)
    try:
        banner = launcher.start()
        repo_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in tmp_path.rglob("*")
            if path.is_file()
        )
        assert banner.session_credential not in repo_text
        assert banner.csrf_token not in repo_text
    finally:
        launcher.stop()


def test_tauri_lib_keeps_loopback_only_defaults() -> None:
    lib = (KIT_ROOT / "desktop" / "src-tauri" / "src" / "lib.rs").read_text(encoding="utf-8")
    launcher_rs = (KIT_ROOT / "desktop" / "src-tauri" / "src" / "launcher.rs").read_text(encoding="utf-8")
    assert "127.0.0.1" in launcher_rs
    assert "0.0.0.0" not in launcher_rs
    assert "ok" in launcher_rs and "app" in launcher_rs
    assert "WebviewUrl::External" in lib


def test_manifest_has_no_absolute_home_paths() -> None:
    manifest = DesktopManifest.from_kit_root(KIT_ROOT)
    for path in (manifest.tauri_conf, manifest.lib_rs, manifest.bundle_script):
        text = path.read_text(encoding="utf-8")
        assert "/Users/" not in text
        assert "password" not in text.lower()

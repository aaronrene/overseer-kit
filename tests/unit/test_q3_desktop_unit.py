"""Unit tests for Track Q / Q3 Tauri desktop packaging."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support import KIT_ROOT
from tools.desktop.banner import StartupBanner, parse_startup_banner_line, parse_startup_stderr
from tools.desktop.constants import (
    CANONICAL_LAUNCHER,
    CANONICAL_SUBCOMMAND,
    DEFAULT_BIND,
    DEFAULT_PORT,
    DESKTOP_IDENTIFIER,
    DESKTOP_PRODUCT_NAME,
    LISTENING_BANNER,
)
from tools.desktop.init_script import build_auth_bootstrap_script
from tools.desktop.launcher import build_launch_argv, resolve_kit_root, resolve_repo_root
from tools.desktop.manifest import DesktopManifest, validate_desktop_manifest


def test_canonical_launcher_constants() -> None:
    assert CANONICAL_LAUNCHER == "ok"
    assert CANONICAL_SUBCOMMAND == "app"
    assert DEFAULT_PORT == 8765
    assert DEFAULT_BIND == "127.0.0.1"
    assert DESKTOP_PRODUCT_NAME == "Overseer Kit"
    assert DESKTOP_IDENTIFIER == "com.overseer.kit.desktop"


def test_build_launch_argv_uses_ok_app(tmp_path: Path) -> None:
    argv = build_launch_argv(kit_root_path=KIT_ROOT, repo_root=tmp_path, port=9999)
    assert argv[0].endswith("/cli/ok")
    assert argv[1:6] == ["app", "--repo", str(tmp_path.resolve()), "--port", "9999"]
    assert argv[-2:] == ["--bind", "127.0.0.1"]


def test_resolve_kit_root_prefers_explicit() -> None:
    assert resolve_kit_root(KIT_ROOT) == KIT_ROOT.resolve()


def test_resolve_repo_root_prefers_explicit(tmp_path: Path) -> None:
    assert resolve_repo_root(kit=KIT_ROOT, explicit=tmp_path) == tmp_path.resolve()


@pytest.mark.parametrize(
    ("line", "field", "value"),
    [
        (LISTENING_BANNER, "listening", LISTENING_BANNER),
        ("url: http://127.0.0.1:8765/", "url", "http://127.0.0.1:8765/"),
        ("session_credential: abc123", "session_credential", "abc123"),
        ("csrf_token: def456", "csrf_token", "def456"),
    ],
)
def test_parse_startup_banner_line(line: str, field: str, value: str) -> None:
    parsed = parse_startup_banner_line(line)
    assert parsed == (field, value)


def test_parse_startup_stderr_complete() -> None:
    lines = [
        "ok app listening\n",
        "url: http://127.0.0.1:8765/\n",
        "session_credential: sess\n",
        "csrf_token: csrf\n",
    ]
    banner = parse_startup_stderr(lines)
    assert banner == StartupBanner(
        url="http://127.0.0.1:8765/",
        session_credential="sess",
        csrf_token="csrf",
    )


def test_parse_startup_stderr_incomplete() -> None:
    assert parse_startup_stderr(["ok app listening\n"]) is None


def test_init_script_uses_json_encoded_secrets() -> None:
    script = build_auth_bootstrap_script(session_credential='a"b', csrf_token="c'd")
    assert json.dumps('a"b') in script
    assert json.dumps("c'd") in script
    assert "localStorage" not in script


def test_desktop_manifest_validates(tmp_path: Path) -> None:
    manifest = DesktopManifest.from_kit_root(KIT_ROOT)
    errors = validate_desktop_manifest(manifest)
    assert errors == []


def test_before_build_command_resolves_from_desktop_cwd() -> None:
    """Tauri runs beforeBuildCommand with cwd=desktop/; path must not escape the kit."""
    conf = json.loads(
        (KIT_ROOT / "desktop" / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8")
    )
    cmd = conf["build"]["beforeBuildCommand"]
    assert "cd ../.." not in cmd
    # Resolve like a shell would from desktop/
    desktop = KIT_ROOT / "desktop"
    script = (desktop / Path(cmd)).resolve() if not cmd.startswith("cd ") else None
    if script is None:
        # Allow `cd .. && ./scripts/...` form
        assert "scripts/bundle-desktop-kit.sh" in cmd
        script = (KIT_ROOT / "scripts" / "bundle-desktop-kit.sh").resolve()
    assert script.is_file(), f"beforeBuildCommand does not resolve to an existing script: {cmd}"
    assert script == (KIT_ROOT / "scripts" / "bundle-desktop-kit.sh").resolve()

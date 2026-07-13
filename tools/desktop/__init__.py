"""Track Q / Q3 Tauri desktop packaging helpers (launcher contract only)."""

from tools.desktop.banner import StartupBanner, parse_startup_banner_line, parse_startup_stderr
from tools.desktop.constants import (
    CANONICAL_LAUNCHER,
    DEFAULT_BIND,
    DEFAULT_PORT,
    DESKTOP_PRODUCT_NAME,
    LISTENING_BANNER,
)
from tools.desktop.init_script import build_auth_bootstrap_script
from tools.desktop.launcher import DesktopLauncher, build_launch_argv, resolve_kit_root
from tools.desktop.manifest import DesktopManifest, validate_desktop_manifest

__all__ = [
    "CANONICAL_LAUNCHER",
    "DEFAULT_BIND",
    "DEFAULT_PORT",
    "DESKTOP_PRODUCT_NAME",
    "LISTENING_BANNER",
    "DesktopLauncher",
    "DesktopManifest",
    "StartupBanner",
    "build_auth_bootstrap_script",
    "build_launch_argv",
    "parse_startup_banner_line",
    "parse_startup_stderr",
    "resolve_kit_root",
    "validate_desktop_manifest",
]

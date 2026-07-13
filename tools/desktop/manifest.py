"""Validate the cross-platform Tauri desktop packaging manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.desktop.constants import (
    CANONICAL_LAUNCHER,
    CANONICAL_SUBCOMMAND,
    DESKTOP_IDENTIFIER,
    DESKTOP_PRODUCT_NAME,
)


@dataclass(frozen=True)
class DesktopManifest:
    """Paths required for Track Q / Q3 desktop packaging."""

    root: Path
    tauri_conf: Path
    cargo_toml: Path
    lib_rs: Path
    launcher_rs: Path
    package_json: Path
    ok_shim: Path
    bundle_script: Path

    @classmethod
    def from_kit_root(cls, kit_root: Path) -> DesktopManifest:
        desktop = kit_root / "desktop"
        return cls(
            root=desktop,
            tauri_conf=desktop / "src-tauri" / "tauri.conf.json",
            cargo_toml=desktop / "src-tauri" / "Cargo.toml",
            lib_rs=desktop / "src-tauri" / "src" / "lib.rs",
            launcher_rs=desktop / "src-tauri" / "src" / "launcher.rs",
            package_json=desktop / "package.json",
            ok_shim=kit_root / "cli" / CANONICAL_LAUNCHER,
            bundle_script=kit_root / "scripts" / "bundle-desktop-kit.sh",
        )


def validate_desktop_manifest(manifest: DesktopManifest) -> list[str]:
    """Return human-readable errors when packaging files are missing or misconfigured."""
    errors: list[str] = []
    for label, path in (
        ("tauri.conf.json", manifest.tauri_conf),
        ("Cargo.toml", manifest.cargo_toml),
        ("lib.rs", manifest.lib_rs),
        ("launcher.rs", manifest.launcher_rs),
        ("package.json", manifest.package_json),
        ("ok shim", manifest.ok_shim),
        ("bundle script", manifest.bundle_script),
    ):
        if not path.is_file():
            errors.append(f"missing {label}: {path}")

    if manifest.tauri_conf.is_file():
        text = manifest.tauri_conf.read_text(encoding="utf-8")
        if DESKTOP_PRODUCT_NAME not in text:
            errors.append(f"tauri.conf.json must name product {DESKTOP_PRODUCT_NAME!r}")
        if DESKTOP_IDENTIFIER not in text:
            errors.append(f"tauri.conf.json must use identifier {DESKTOP_IDENTIFIER!r}")

    if manifest.lib_rs.is_file():
        lib = manifest.lib_rs.read_text(encoding="utf-8")
        if "mod launcher" not in lib:
            errors.append("lib.rs must wire the desktop launcher module")
        if "WebviewUrl::External" not in lib:
            errors.append("lib.rs must load the loopback UI in an external webview")

    if manifest.launcher_rs.is_file():
        launcher = manifest.launcher_rs.read_text(encoding="utf-8")
        if CANONICAL_LAUNCHER not in launcher or CANONICAL_SUBCOMMAND not in launcher:
            errors.append("launcher.rs must invoke canonical ok app launcher")
        if "127.0.0.1" not in launcher:
            errors.append("launcher.rs must keep loopback-only packaging defaults")

    if manifest.bundle_script.is_file():
        script = manifest.bundle_script.read_text(encoding="utf-8")
        for needle in ("cli", "adapters", "tools"):
            if needle not in script:
                errors.append(f"bundle script must copy {needle}")

    return errors

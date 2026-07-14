"""Version alignment checker (§QR.8).

Verifies equality (after trim) of VERSION, desktop package.json, Cargo.toml,
tauri.conf.json, and the release tag / dispatch version. Pure — never writes.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


class VersionAlignError(ValueError):
    """Raised when version strings are missing or mismatched."""


_CARGO_VERSION_RE = re.compile(
    r'(?m)^\[package\]\s*\n(?:.*\n)*?^version\s*=\s*"([^"]+)"',
)


@dataclass(frozen=True)
class VersionSources:
    """Collected version strings from kit tree files."""

    root_version: str
    package_json: str
    cargo_toml: str
    tauri_conf: str


def read_root_version(kit_root: Path) -> str:
    """Return trimmed contents of ``VERSION``."""
    path = kit_root / "VERSION"
    if not path.is_file():
        raise VersionAlignError(f"missing VERSION file: {path}")
    return path.read_text(encoding="utf-8").strip()


def read_package_json_version(kit_root: Path) -> str:
    """Return ``desktop/package.json`` version."""
    path = kit_root / "desktop" / "package.json"
    if not path.is_file():
        raise VersionAlignError(f"missing package.json: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise VersionAlignError("desktop/package.json missing version string")
    return version.strip()


def read_cargo_toml_version(kit_root: Path) -> str:
    """Return ``[package].version`` from desktop Cargo.toml."""
    path = kit_root / "desktop" / "src-tauri" / "Cargo.toml"
    if not path.is_file():
        raise VersionAlignError(f"missing Cargo.toml: {path}")
    text = path.read_text(encoding="utf-8")
    match = _CARGO_VERSION_RE.search(text)
    if match is None:
        # Fallback: first package version line after [package]
        in_package = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "[package]":
                in_package = True
                continue
            if in_package and stripped.startswith("[") and stripped.endswith("]"):
                break
            if in_package and stripped.startswith("version"):
                _, _, raw = stripped.partition("=")
                return raw.strip().strip('"').strip("'")
        raise VersionAlignError("Cargo.toml missing package.version")
    return match.group(1).strip()


def read_tauri_conf_version(kit_root: Path) -> str:
    """Return ``version`` from tauri.conf.json."""
    path = kit_root / "desktop" / "src-tauri" / "tauri.conf.json"
    if not path.is_file():
        raise VersionAlignError(f"missing tauri.conf.json: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise VersionAlignError("tauri.conf.json missing version string")
    return version.strip()


def collect_versions(kit_root: Path) -> VersionSources:
    """Load all four tree-side version sources."""
    return VersionSources(
        root_version=read_root_version(kit_root),
        package_json=read_package_json_version(kit_root),
        cargo_toml=read_cargo_toml_version(kit_root),
        tauri_conf=read_tauri_conf_version(kit_root),
    )


def normalize_tag(tag: str) -> str:
    """Strip a leading ``v`` from a git tag name."""
    tag = tag.strip()
    if tag.startswith("v") or tag.startswith("V"):
        return tag[1:]
    return tag


def check_version_alignment(
    kit_root: Path,
    *,
    tag: str | None = None,
    dispatch_version: str | None = None,
) -> str:
    """Fail closed unless all version sources equal.

    Parameters
    ----------
    kit_root:
        Repository root containing ``VERSION`` and ``desktop/``.
    tag:
        Optional git tag (``v0.1.0`` or ``0.1.0``). When set, must equal VERSION.
    dispatch_version:
        Optional ``workflow_dispatch`` version input. When set, must equal VERSION.

    Returns
    -------
    str
        The aligned version string.

    Raises
    ------
    VersionAlignError
        On any mismatch or missing file.
    """
    sources = collect_versions(kit_root)
    values = {
        "VERSION": sources.root_version,
        "desktop/package.json": sources.package_json,
        "desktop/src-tauri/Cargo.toml": sources.cargo_toml,
        "desktop/src-tauri/tauri.conf.json": sources.tauri_conf,
    }
    expected = sources.root_version
    for label, value in values.items():
        if value != expected:
            raise VersionAlignError(
                f"version mismatch: {label}={value!r} != VERSION={expected!r}"
            )

    if tag is not None:
        tag_version = normalize_tag(tag)
        if tag_version != expected:
            raise VersionAlignError(
                f"version mismatch: git tag {tag!r} → {tag_version!r} != VERSION={expected!r}"
            )

    if dispatch_version is not None:
        dv = dispatch_version.strip()
        if dv != expected:
            raise VersionAlignError(
                f"version mismatch: dispatch version={dv!r} != VERSION={expected!r}"
            )

    return expected

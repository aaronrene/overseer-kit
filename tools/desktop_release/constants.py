"""Frozen constants for Q3-release desktop installers (§QR.4–§QR.8)."""

from __future__ import annotations

PRODUCT_NAME = "Overseer Kit"
PRODUCT_IDENTIFIER = "com.overseer.kit.desktop"
MANIFEST_SCHEMA_VERSION = 1
MANIFEST_FILENAME_TEMPLATE = "overseer-kit-desktop-{version}-manifest.json"
SHA256SUMS_FILENAME = "SHA256SUMS.txt"

PLATFORMS = frozenset({"macos", "windows", "linux"})
SIGNING_STATUSES = frozenset({"signed", "unsigned", "unavailable"})
SIGNING_METHODS = frozenset(
    {
        "developer_id_notarized",
        "authenticode",
        "minisign_detached",
        "gpg_detached",
        "none",
    }
)

# Platform → allowed methods when status is ``signed`` (§QR.5 / §QR.7.1).
SIGNED_METHODS_BY_PLATFORM: dict[str, frozenset[str]] = {
    "macos": frozenset({"developer_id_notarized"}),
    "windows": frozenset({"authenticode"}),
    "linux": frozenset({"minisign_detached", "gpg_detached"}),
}

# §QR.6.2 — exact GitHub Actions secret names.
APPLE_SECRETS = (
    "APPLE_CERTIFICATE",
    "APPLE_CERTIFICATE_PASSWORD",
    "APPLE_ID",
    "APPLE_TEAM_ID",
    "APPLE_APP_SPECIFIC_PASSWORD",
    "APPLE_SIGNING_IDENTITY",
)
APPLE_API_KEY_SECRETS = (
    "APPLE_API_KEY",
    "APPLE_API_KEY_ID",
    "APPLE_API_ISSUER",
    "APPLE_TEAM_ID",
)
WINDOWS_SECRETS = (
    "WINDOWS_CERTIFICATE",
    "WINDOWS_CERTIFICATE_PASSWORD",
)
LINUX_SECRETS = (
    "LINUX_SIGNING_KEY",
    "LINUX_SIGNING_KEY_PASSWORD",
)

ALL_RELEASE_SECRET_NAMES = frozenset(
    (*APPLE_SECRETS, *APPLE_API_KEY_SECRETS, *WINDOWS_SECRETS, *LINUX_SECRETS)
)

# Bundle script closed allowlist (§QR.6.3) — dirs + files relative to kit root.
BUNDLE_ALLOWLIST_DIRS = frozenset({"adapters", "cli", "tools", "policy", "templates", "cursor"})
BUNDLE_ALLOWLIST_FILES = frozenset({"VERSION", "pyproject.toml"})

# Publish allowlist extensions / names (§QR.4.5).
ALLOWED_INSTALLER_SUFFIXES = (".dmg", ".msi", ".AppImage")
ALLOWED_SIDECAR_SUFFIXES = (".AppImage.minisig", ".AppImage.asc")

PUBLIC_KEY_ALLOWED_SUFFIXES = (".pub", ".asc", ".minisign.pub")
PRIVATE_KEY_BASENAME_MARKERS = (
    "private",
    ".p12",
    ".pfx",
    ".key",
    "secret",
    "seckey",
)

# Stress / performance bounds documented for §QR.13.
MANIFEST_ARTIFACT_CAP = 50
VERSION_ALIGN_PERF_BOUND_SECONDS = 2.0

MACOS_PINNED_RUNNERS = frozenset({"macos-14", "macos-15"})
LINUX_PINNED_RUNNERS = frozenset({"ubuntu-22.04", "ubuntu-24.04"})

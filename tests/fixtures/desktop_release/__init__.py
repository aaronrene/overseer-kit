"""Shared fixtures for Q3-release desktop installer tests (§QR.13)."""

from __future__ import annotations

from pathlib import Path

from tests.support import KIT_ROOT

RELEASE_WORKFLOW = KIT_ROOT / ".github" / "workflows" / "desktop-release.yml"
SMOKE_WORKFLOW = KIT_ROOT / ".github" / "workflows" / "desktop-build-smoke.yml"
RELEASE_TEMPLATE = KIT_ROOT / "templates" / "ci" / "desktop-release-github-actions.yml"
BUNDLE_SCRIPT = KIT_ROOT / "scripts" / "bundle-desktop-kit.sh"
RUNBOOK = KIT_ROOT / "docs" / "TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md"
DESKTOP_KEYS = KIT_ROOT / "desktop" / "keys"
PUBLIC_KEY = DESKTOP_KEYS / "release.minisign.pub"

GIT_SHA_FIXTURE = "a" * 40


def sample_signed_artifacts(version: str = "0.1.0") -> list[dict]:
    """Return three signed platform artifact dicts for schema tests."""
    return [
        {
            "platform": "macos",
            "filename": f"Overseer Kit_{version}_aarch64.dmg",
            "sha256": "b" * 64,
            "arch": "aarch64",
            "signing": {"status": "signed", "method": "developer_id_notarized"},
        },
        {
            "platform": "windows",
            "filename": f"Overseer Kit_{version}_x64_en-US.msi",
            "sha256": "c" * 64,
            "arch": "x86_64",
            "signing": {"status": "signed", "method": "authenticode"},
        },
        {
            "platform": "linux",
            "filename": f"Overseer Kit_{version}_amd64.AppImage",
            "sha256": "d" * 64,
            "arch": "x86_64",
            "signing": {"status": "signed", "method": "minisign_detached"},
        },
    ]


def write_artifact_files(directory: Path, artifacts: list[dict]) -> list[Path]:
    """Write tiny fixture files named like release artifacts; return paths."""
    directory.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for item in artifacts:
        path = directory / item["filename"]
        # Distinct bytes per platform so hashes differ.
        path.write_bytes(f"fixture:{item['platform']}:{item['filename']}\n".encode("utf-8"))
        paths.append(path)
    return paths

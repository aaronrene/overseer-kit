"""Fixture finalize path for release artifacts (§QR.12 / §QR.13 e2e)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.desktop_release.allowlist import refuse_disallowed_asset
from tools.desktop_release.checksums import parse_sha256sums, sha256_file, write_sha256sums
from tools.desktop_release.constants import (
    MANIFEST_ARTIFACT_CAP,
    MANIFEST_FILENAME_TEMPLATE,
    SHA256SUMS_FILENAME,
)
from tools.desktop_release.manifest import ManifestError, build_manifest, canonical_manifest_bytes


class FinalizeError(ValueError):
    """Raised when release finalize refuses (missing secrets, bad schema, etc.)."""


@dataclass(frozen=True)
class ArtifactInput:
    """One platform artifact for finalize."""

    platform: str
    path: Path
    signing_status: str
    signing_method: str
    arch: str | None = None


def require_signing_secrets(
    *,
    publish: bool,
    platform: str,
    secrets_present: Mapping[str, bool],
) -> None:
    """Fail closed when release publish lacks required platform secrets."""
    if not publish:
        return
    required: tuple[str, ...]
    if platform == "macos":
        # Password mode OR API-key mode (§QR.6.2).
        password_mode = all(
            secrets_present.get(name, False)
            for name in (
                "APPLE_CERTIFICATE",
                "APPLE_CERTIFICATE_PASSWORD",
                "APPLE_ID",
                "APPLE_TEAM_ID",
                "APPLE_APP_SPECIFIC_PASSWORD",
                "APPLE_SIGNING_IDENTITY",
            )
        )
        api_mode = all(
            secrets_present.get(name, False)
            for name in (
                "APPLE_CERTIFICATE",
                "APPLE_CERTIFICATE_PASSWORD",
                "APPLE_API_KEY",
                "APPLE_API_KEY_ID",
                "APPLE_API_ISSUER",
                "APPLE_TEAM_ID",
                "APPLE_SIGNING_IDENTITY",
            )
        )
        if not (password_mode or api_mode):
            raise FinalizeError("missing Apple signing secrets — fail closed")
        return
    if platform == "windows":
        required = ("WINDOWS_CERTIFICATE", "WINDOWS_CERTIFICATE_PASSWORD")
    elif platform == "linux":
        required = ("LINUX_SIGNING_KEY",)
    else:
        raise FinalizeError(f"unknown platform: {platform!r}")
    missing = [name for name in required if not secrets_present.get(name, False)]
    if missing:
        raise FinalizeError(f"missing {platform} signing secrets: {', '.join(missing)}")


def finalize_release_artifacts(
    *,
    version: str,
    git_sha: str,
    artifacts: Sequence[ArtifactInput],
    output_dir: Path,
    publish: bool = True,
    allow_partial: bool = False,
    secrets_present: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Build manifest + SHA256SUMS from artifact files (fixture-friendly).

    When ``publish`` is True, requires platform signing secrets via
    ``secrets_present``. When ``allow_partial`` is False, every artifact must
    have ``signing_status == "signed"``.
    """
    secrets = secrets_present or {}
    if len(artifacts) > MANIFEST_ARTIFACT_CAP:
        raise FinalizeError(
            f"artifact count {len(artifacts)} exceeds cap {MANIFEST_ARTIFACT_CAP}"
        )

    for artifact in artifacts:
        require_signing_secrets(
            publish=publish,
            platform=artifact.platform,
            secrets_present=secrets,
        )
        if publish and not allow_partial and artifact.signing_status != "signed":
            raise FinalizeError(
                f"artifact {artifact.path.name} not signed — fail closed "
                f"(status={artifact.signing_status!r})"
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_artifacts: list[dict[str, Any]] = []
    sums_entries: list[tuple[str, str]] = []

    for artifact in artifacts:
        if not artifact.path.is_file():
            raise FinalizeError(f"artifact missing: {artifact.path}")
        digest = sha256_file(artifact.path)
        filename = artifact.path.name
        refuse_disallowed_asset(filename, version=version)
        entry: dict[str, Any] = {
            "platform": artifact.platform,
            "filename": filename,
            "sha256": digest,
            "signing": {
                "status": artifact.signing_status,
                "method": artifact.signing_method,
            },
        }
        if artifact.arch is not None:
            entry["arch"] = artifact.arch
        manifest_artifacts.append(entry)
        sums_entries.append((digest, filename))

    try:
        manifest = build_manifest(
            version=version,
            git_sha=git_sha,
            artifacts=manifest_artifacts,
        )
    except ManifestError as exc:
        raise FinalizeError(str(exc)) from exc

    manifest_name = MANIFEST_FILENAME_TEMPLATE.format(version=version)
    refuse_disallowed_asset(manifest_name, version=version)
    manifest_path = output_dir / manifest_name
    manifest_path.write_bytes(canonical_manifest_bytes(manifest))

    sums_path = output_dir / SHA256SUMS_FILENAME
    write_sha256sums(sums_path, sums_entries)

    # Integrity: sha256 fields must match SHA256SUMS.txt
    parsed = parse_sha256sums(sums_path.read_text(encoding="utf-8"))
    for entry in manifest["artifacts"]:
        filename = entry["filename"]
        if parsed.get(filename) != entry["sha256"]:
            raise FinalizeError(f"checksum mismatch for {filename}")

    return manifest

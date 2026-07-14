"""Data-integrity tests for Q3-release desktop installers (§QR.13)."""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.desktop_release import (
    GIT_SHA_FIXTURE,
    sample_signed_artifacts,
    write_artifact_files,
)
from tools.desktop_release.checksums import parse_sha256sums
from tools.desktop_release.constants import MANIFEST_FILENAME_TEMPLATE, SHA256SUMS_FILENAME
from tools.desktop_release.finalize import ArtifactInput, finalize_release_artifacts
from tools.desktop_release.manifest import canonical_manifest_bytes, validate_manifest
from tools.desktop_release.version_align import check_version_alignment
from tests.support import KIT_ROOT


FULL_SECRETS = {
    "APPLE_CERTIFICATE": True,
    "APPLE_CERTIFICATE_PASSWORD": True,
    "APPLE_ID": True,
    "APPLE_TEAM_ID": True,
    "APPLE_APP_SPECIFIC_PASSWORD": True,
    "APPLE_SIGNING_IDENTITY": True,
    "WINDOWS_CERTIFICATE": True,
    "WINDOWS_CERTIFICATE_PASSWORD": True,
    "LINUX_SIGNING_KEY": True,
}


def test_twin_manifest_byte_identical(tmp_path: Path) -> None:
    arts = sample_signed_artifacts()
    paths = write_artifact_files(tmp_path / "bins", arts)
    inputs = [
        ArtifactInput(
            platform=a["platform"],
            path=p,
            signing_status="signed",
            signing_method=a["signing"]["method"],
            arch=a.get("arch"),
        )
        for a, p in zip(arts, paths, strict=True)
    ]
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    m1 = finalize_release_artifacts(
        version="0.1.0",
        git_sha=GIT_SHA_FIXTURE,
        artifacts=inputs,
        output_dir=out_a,
        publish=True,
        secrets_present=FULL_SECRETS,
    )
    m2 = finalize_release_artifacts(
        version="0.1.0",
        git_sha=GIT_SHA_FIXTURE,
        artifacts=inputs,
        output_dir=out_b,
        publish=True,
        secrets_present=FULL_SECRETS,
    )
    assert canonical_manifest_bytes(m1) == canonical_manifest_bytes(m2)
    name = MANIFEST_FILENAME_TEMPLATE.format(version="0.1.0")
    assert (out_a / name).read_bytes() == (out_b / name).read_bytes()


def test_manifest_sha256_matches_sums(tmp_path: Path) -> None:
    arts = sample_signed_artifacts()
    paths = write_artifact_files(tmp_path / "bins", arts)
    inputs = [
        ArtifactInput(
            platform=a["platform"],
            path=p,
            signing_status="signed",
            signing_method=a["signing"]["method"],
        )
        for a, p in zip(arts, paths, strict=True)
    ]
    out = tmp_path / "dist"
    manifest = finalize_release_artifacts(
        version="0.1.0",
        git_sha=GIT_SHA_FIXTURE,
        artifacts=inputs,
        output_dir=out,
        publish=True,
        secrets_present=FULL_SECRETS,
    )
    parsed = parse_sha256sums((out / SHA256SUMS_FILENAME).read_text(encoding="utf-8"))
    for entry in manifest["artifacts"]:
        assert parsed[entry["filename"]] == entry["sha256"]
    # Re-validate after rewrite
    rewritten = out / MANIFEST_FILENAME_TEMPLATE.format(version="0.1.0")
    validate_manifest(__import__("json").loads(rewritten.read_text(encoding="utf-8")))


def test_version_align_is_pure() -> None:
    before = {
        p: p.read_bytes()
        for p in (
            KIT_ROOT / "VERSION",
            KIT_ROOT / "desktop" / "package.json",
            KIT_ROOT / "desktop" / "src-tauri" / "Cargo.toml",
            KIT_ROOT / "desktop" / "src-tauri" / "tauri.conf.json",
        )
    }
    check_version_alignment(KIT_ROOT)
    after = {p: p.read_bytes() for p in before}
    assert before == after

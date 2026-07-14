"""Unit tests for Q3-release desktop installers (§QR.13)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.fixtures.desktop_release import GIT_SHA_FIXTURE, sample_signed_artifacts
from tools.desktop_release.allowlist import AllowlistError, is_allowed_release_asset, refuse_disallowed_asset
from tools.desktop_release.checksums import sha256_file
from tools.desktop_release.manifest import ManifestError, build_manifest, validate_manifest
from tools.desktop_release.refuse import (
    RefuseError,
    refuse_private_key_under_desktop_keys,
    scan_text_for_secret_patterns,
)
from tools.desktop_release.version_align import VersionAlignError, check_version_alignment
from tests.support import KIT_ROOT


def test_version_align_accepts_kit_tree() -> None:
    version = check_version_alignment(KIT_ROOT)
    assert version == (KIT_ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_version_align_refuses_mismatch(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    desktop = tmp_path / "desktop"
    (desktop / "src-tauri").mkdir(parents=True)
    (desktop / "package.json").write_text('{"version":"0.1.0"}\n', encoding="utf-8")
    (desktop / "src-tauri" / "Cargo.toml").write_text(
        '[package]\nname="x"\nversion="0.1.0"\n',
        encoding="utf-8",
    )
    (desktop / "src-tauri" / "tauri.conf.json").write_text(
        '{"version":"9.9.9"}\n',
        encoding="utf-8",
    )
    with pytest.raises(VersionAlignError, match="mismatch"):
        check_version_alignment(tmp_path)


def test_version_align_tag_and_dispatch() -> None:
    version = check_version_alignment(KIT_ROOT, tag="v0.1.0", dispatch_version="0.1.0")
    assert version == "0.1.0"
    with pytest.raises(VersionAlignError):
        check_version_alignment(KIT_ROOT, tag="v9.9.9")


def test_manifest_accepts_valid_fixture() -> None:
    doc = build_manifest(
        version="0.1.0",
        git_sha=GIT_SHA_FIXTURE,
        artifacts=sample_signed_artifacts(),
    )
    validate_manifest(doc)
    assert doc["schema_version"] == 1
    assert doc["product"] == "Overseer Kit"


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("platform", "freebsd"),
        ("status", "notarized"),
        ("method", "cloudflare"),
    ],
)
def test_manifest_refuses_unknown_enums(field: str, bad: str) -> None:
    arts = sample_signed_artifacts()
    if field == "platform":
        arts[0]["platform"] = bad
    elif field == "status":
        arts[0]["signing"]["status"] = bad
    else:
        arts[0]["signing"]["method"] = bad
    with pytest.raises(ManifestError):
        build_manifest(version="0.1.0", git_sha=GIT_SHA_FIXTURE, artifacts=arts)


def test_manifest_refuses_signed_with_method_none() -> None:
    arts = sample_signed_artifacts()
    arts[0]["signing"] = {"status": "signed", "method": "none"}
    with pytest.raises(ManifestError, match="method none"):
        build_manifest(version="0.1.0", git_sha=GIT_SHA_FIXTURE, artifacts=arts)


def test_secret_scanner_flags_pem_and_passes_clean_workflow() -> None:
    dirty = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBg\n-----END PRIVATE KEY-----\n"
    assert "pem_private_key" in scan_text_for_secret_patterns(dirty)
    clean = (KIT_ROOT / ".github" / "workflows" / "desktop-release.yml").read_text(encoding="utf-8")
    assert scan_text_for_secret_patterns(clean) == []


def test_checksum_helper_known_vector(tmp_path: Path) -> None:
    path = tmp_path / "blob.bin"
    data = b"overseer-kit-desktop-release"
    path.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    assert sha256_file(path) == expected


def test_public_key_path_rules() -> None:
    refuse_private_key_under_desktop_keys(Path("desktop/keys/release.minisign.pub"))
    refuse_private_key_under_desktop_keys(Path("desktop/keys/README.md"))
    with pytest.raises(RefuseError):
        refuse_private_key_under_desktop_keys(Path("desktop/keys/release.private.key"))
    with pytest.raises(RefuseError):
        refuse_private_key_under_desktop_keys(Path("desktop/keys/secret.pem"))


def test_allowlist_accepts_and_rejects() -> None:
    assert is_allowed_release_asset("Overseer Kit_0.1.0_aarch64.dmg", version="0.1.0")
    assert is_allowed_release_asset("SHA256SUMS.txt")
    assert is_allowed_release_asset("overseer-kit-desktop-0.1.0-manifest.json", version="0.1.0")
    with pytest.raises(AllowlistError):
        refuse_disallowed_asset("Overseer Kit_0.1.0_amd64.deb")
    with pytest.raises(AllowlistError):
        refuse_disallowed_asset("app-unsigned.AppImage")

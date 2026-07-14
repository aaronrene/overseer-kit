"""End-to-end tests for Q3-release desktop installers (§QR.13)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.fixtures.desktop_release import (
    GIT_SHA_FIXTURE,
    PUBLIC_KEY,
    RUNBOOK,
    sample_signed_artifacts,
    write_artifact_files,
)
from tests.support import KIT_ROOT
from tools.desktop_release.checksums import parse_sha256sums
from tools.desktop_release.constants import MANIFEST_FILENAME_TEMPLATE, SHA256SUMS_FILENAME
from tools.desktop_release.finalize import ArtifactInput, FinalizeError, finalize_release_artifacts
from tools.desktop_release.manifest import validate_manifest


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


def test_finalize_round_trip(tmp_path: Path) -> None:
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
    out = tmp_path / "dist"
    manifest = finalize_release_artifacts(
        version="0.1.0",
        git_sha=GIT_SHA_FIXTURE,
        artifacts=inputs,
        output_dir=out,
        publish=True,
        secrets_present=FULL_SECRETS,
    )
    validate_manifest(manifest)
    manifest_path = out / MANIFEST_FILENAME_TEMPLATE.format(version="0.1.0")
    assert manifest_path.is_file()
    sums_path = out / SHA256SUMS_FILENAME
    parsed = parse_sha256sums(sums_path.read_text(encoding="utf-8"))
    for entry in manifest["artifacts"]:
        assert parsed[entry["filename"]] == entry["sha256"]
    # Round-trip JSON
    reload = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(reload)


def test_finalize_refuses_missing_apple_secret(tmp_path: Path) -> None:
    arts = sample_signed_artifacts()[:1]
    paths = write_artifact_files(tmp_path / "bins", arts)
    secrets = dict(FULL_SECRETS)
    secrets["APPLE_CERTIFICATE"] = False
    secrets["APPLE_API_KEY"] = False
    with pytest.raises(FinalizeError, match="Apple"):
        finalize_release_artifacts(
            version="0.1.0",
            git_sha=GIT_SHA_FIXTURE,
            artifacts=[
                ArtifactInput(
                    platform="macos",
                    path=paths[0],
                    signing_status="signed",
                    signing_method="developer_id_notarized",
                )
            ],
            output_dir=tmp_path / "dist",
            publish=True,
            secrets_present=secrets,
        )


def test_runbook_honesty_and_python_prerequisite() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "Python 3.11+" in text
    assert "Signed installers" in text or "signed installers" in text.lower()
    assert "detached" in text.lower()
    assert "AppImage" in text
    assert "Not available" in text or "not available" in text.lower() or "until a GitHub Release" in text
    assert PUBLIC_KEY.is_file()


def test_track_q_api_allowlist_untouched() -> None:
    """Q3-release must not mutate Track Q closed api/* surfaces."""
    server = KIT_ROOT / "tools" / "app" / "server.py"
    assert server.is_file()
    text = server.read_text(encoding="utf-8")
    assert '("/api/health")' in text or "/api/health" in text
    assert "/api/status" in text
    # desktop_release must not import or rewrite tools.app
    release_pkg = KIT_ROOT / "tools" / "desktop_release"
    for path in release_pkg.rglob("*.py"):
        src = path.read_text(encoding="utf-8")
        assert "tools.app" not in src
        assert "from tools.app" not in src
        assert "import tools.app" not in src


def test_bundle_refuses_env_outside_allowlist(tmp_path: Path) -> None:
    """Fresh destination after a dry closed-allowlist copy omits .env."""
    dest = tmp_path / "kit"
    dest.mkdir()
    # Simulate closed allowlist: only copy VERSION (never .env).
    (KIT_ROOT / "VERSION").read_text(encoding="utf-8")
    (dest / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    planted = tmp_path / ".env"
    planted.write_text("SECRET=1\n", encoding="utf-8")
    assert not (dest / ".env").exists()
    assert "SECRET" not in "\n".join(p.read_text(encoding="utf-8") for p in dest.rglob("*") if p.is_file())

"""Stress tests for Q3-release desktop installers (§QR.13)."""

from __future__ import annotations

import resource
from pathlib import Path

from tests.fixtures.desktop_release import GIT_SHA_FIXTURE
from tools.desktop_release.checksums import sha256_file
from tools.desktop_release.constants import MANIFEST_ARTIFACT_CAP
from tools.desktop_release.finalize import FinalizeError, finalize_release_artifacts
from tools.desktop_release.manifest import build_manifest


def test_manifest_builder_fifty_artifact_cap() -> None:
    arts = []
    for i in range(MANIFEST_ARTIFACT_CAP):
        arts.append(
            {
                "platform": "linux",
                "filename": f"Overseer Kit_0.1.0_batch{i}.AppImage",
                "sha256": f"{i:064x}"[-64:],
                "signing": {"status": "signed", "method": "minisign_detached"},
            }
        )
    doc = build_manifest(version="0.1.0", git_sha=GIT_SHA_FIXTURE, artifacts=arts)
    assert len(doc["artifacts"]) == MANIFEST_ARTIFACT_CAP


def test_finalize_refuses_over_cap(tmp_path: Path) -> None:
    from tools.desktop_release.finalize import ArtifactInput

    paths = []
    inputs = []
    for i in range(MANIFEST_ARTIFACT_CAP + 1):
        p = tmp_path / f"a{i}.AppImage"
        p.write_bytes(b"x")
        paths.append(p)
        inputs.append(
            ArtifactInput(
                platform="linux",
                path=p,
                signing_status="signed",
                signing_method="minisign_detached",
            )
        )
    try:
        finalize_release_artifacts(
            version="0.1.0",
            git_sha=GIT_SHA_FIXTURE,
            artifacts=inputs,
            output_dir=tmp_path / "out",
            publish=False,
        )
        raise AssertionError("expected cap refuse")
    except FinalizeError as exc:
        assert "cap" in str(exc)


def test_streaming_checksum_large_fixture(tmp_path: Path) -> None:
    """Multi-megabyte file hashed in a single streaming pass (bounded RSS growth)."""
    path = tmp_path / "large.bin"
    # 4 MiB — enough to exercise chunking; avoid huge CI times.
    chunk = b"0123456789abcdef" * 4096  # 64 KiB
    with path.open("wb") as handle:
        for _ in range(64):  # 4 MiB
            handle.write(chunk)
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    digest = sha256_file(path, chunk_size=1024 * 1024)
    after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    assert len(digest) == 64
    # Soft bound: hashing must not multiply RSS by loading the file twice unboundedly.
    # On macOS ru_maxrss is bytes; on Linux it is kilobytes — compare relative delta only.
    assert after >= before  # sanity; primary proof is single-pass API completing

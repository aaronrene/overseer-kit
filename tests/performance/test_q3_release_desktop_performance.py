"""Performance tests for Q3-release desktop installers (§QR.13)."""

from __future__ import annotations

import time
from pathlib import Path

from tests.fixtures.desktop_release import GIT_SHA_FIXTURE, RELEASE_WORKFLOW, sample_signed_artifacts
from tools.desktop_release.constants import VERSION_ALIGN_PERF_BOUND_SECONDS
from tools.desktop_release.manifest import build_manifest, validate_manifest
from tools.desktop_release.refuse import scan_text_for_secret_patterns
from tools.desktop_release.version_align import check_version_alignment
from tests.support import KIT_ROOT


def test_version_align_and_manifest_within_bound() -> None:
    start = time.perf_counter()
    check_version_alignment(KIT_ROOT)
    doc = build_manifest(
        version="0.1.0",
        git_sha=GIT_SHA_FIXTURE,
        artifacts=sample_signed_artifacts(),
    )
    validate_manifest(doc)
    elapsed = time.perf_counter() - start
    assert elapsed <= VERSION_ALIGN_PERF_BOUND_SECONDS, elapsed


def test_secret_scan_bounded_to_release_workflow_paths() -> None:
    """Scan release workflow paths only — not a full-repo secret hunt."""
    paths = [
        RELEASE_WORKFLOW,
        KIT_ROOT / ".github" / "workflows" / "desktop-build-smoke.yml",
        KIT_ROOT / "templates" / "ci" / "desktop-release-github-actions.yml",
    ]
    start = time.perf_counter()
    for path in paths:
        assert path.is_file()
        assert scan_text_for_secret_patterns(path.read_text(encoding="utf-8")) == []
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, elapsed

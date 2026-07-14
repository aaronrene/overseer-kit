"""Desktop installer release helpers (Q3-release / §QR.11).

Pure Python library for version alignment, release manifests, checksums,
publish allowlisting, and secret-pattern refuse — used by CI and tests.
No network I/O required for unit/integration suites.
"""

from __future__ import annotations

from tools.desktop_release.allowlist import is_allowed_release_asset, refuse_disallowed_asset
from tools.desktop_release.checksums import sha256_file, write_sha256sums
from tools.desktop_release.finalize import FinalizeError, finalize_release_artifacts
from tools.desktop_release.manifest import (
    ManifestError,
    build_manifest,
    canonical_manifest_bytes,
    validate_manifest,
)
from tools.desktop_release.refuse import (
    RefuseError,
    refuse_private_key_under_desktop_keys,
    refuse_secret_write_to_repo,
    scan_text_for_secret_patterns,
)
from tools.desktop_release.version_align import VersionAlignError, check_version_alignment

__all__ = [
    "FinalizeError",
    "ManifestError",
    "RefuseError",
    "VersionAlignError",
    "build_manifest",
    "canonical_manifest_bytes",
    "check_version_alignment",
    "finalize_release_artifacts",
    "is_allowed_release_asset",
    "refuse_disallowed_asset",
    "refuse_private_key_under_desktop_keys",
    "refuse_secret_write_to_repo",
    "scan_text_for_secret_patterns",
    "sha256_file",
    "validate_manifest",
    "write_sha256sums",
]

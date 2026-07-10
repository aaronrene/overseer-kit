"""Kit drift computation for ``overseer status``."""

from __future__ import annotations

from cli.footprint import FootprintFile
from cli.sync_classify import Classification, classify_footprint
from cli.version_lock import VersionLock


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse a simple ``major.minor.patch`` semver string."""
    parts = version.strip().split(".")
    if len(parts) != 3:
        raise ValueError(f"invalid semver: {version!r}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def compare_semver(left: str, right: str) -> int:
    """Compare semver strings; return -1, 0, or 1."""
    lv = parse_semver(left)
    rv = parse_semver(right)
    if lv < rv:
        return -1
    if lv > rv:
        return 1
    return 0


def compute_drift(
    *,
    cli_version: str,
    lock: VersionLock | None,
    rendered: list[FootprintFile],
    repo_root,
) -> dict:
    """Return the frozen drift report object."""
    if lock is None:
        return {
            "status": "behind",
            "kit_version": cli_version,
            "lock_version": None,
            "changed_files": [f.destination for f in rendered],
        }

    cmp_result = compare_semver(lock.kit_version, cli_version)
    if cmp_result == 0:
        status = "current"
        changed: list[str] = []
    elif cmp_result < 0:
        status = "behind"
        classified = classify_footprint(rendered, lock, repo_root)
        changed = [
            row.destination
            for row in classified
            if row.classification
            in {Classification.KIT_UPDATED, Classification.BOTH_CHANGED, Classification.MISSING}
        ]
    else:
        status = "ahead"
        changed = []

    return {
        "status": status,
        "kit_version": cli_version,
        "lock_version": lock.kit_version,
        "changed_files": changed,
    }

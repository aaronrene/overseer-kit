"""Footprint coverage gate — resolve destinations must appear in version.lock (§LT.3.1)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.config import OverseerConfig
from cli.footprint import FootprintFile, resolve_footprint
from cli.version_lock import LockError, VersionLock, lock_path, read_version_lock

REMEDIATION = "ok sync"


@dataclass(frozen=True)
class FootprintCoverageReport:
    """Result of comparing resolve_footprint destinations to version.lock paths."""

    state: str  # ok | missing_from_lock | not_applicable
    message: str
    remediation: str | None
    missing: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.state in {"ok", "not_applicable"}


def check_footprint_coverage(
    repo_root: Path,
    config: OverseerConfig,
    *,
    lock: VersionLock | None = None,
    rendered: list[FootprintFile] | None = None,
    kit: Path | None = None,
) -> FootprintCoverageReport:
    """Return coverage state for resolve destinations vs lock footprint list."""
    if lock is None:
        path = lock_path(repo_root)
        if not path.is_file():
            return FootprintCoverageReport(
                state="not_applicable",
                message="no version.lock yet — coverage not applicable",
                remediation=None,
            )
        try:
            lock = read_version_lock(path)
        except LockError as exc:
            return FootprintCoverageReport(
                state="not_applicable",
                message=f"version.lock unreadable — coverage not applicable: {exc}",
                remediation=None,
            )

    if not lock.footprint:
        return FootprintCoverageReport(
            state="not_applicable",
            message="version.lock footprint list is empty — coverage not applicable",
            remediation=None,
        )

    if rendered is None:
        rendered = resolve_footprint(config, kit=kit)

    lock_paths = {entry.path for entry in lock.footprint}
    missing = tuple(
        sorted(item.destination for item in rendered if item.destination not in lock_paths)
    )

    if missing:
        listed = ", ".join(missing)
        return FootprintCoverageReport(
            state="missing_from_lock",
            message=(
                f"{len(missing)} resolve footprint destination(s) absent from "
                f"version.lock: {listed}"
            ),
            remediation=REMEDIATION,
            missing=missing,
        )

    return FootprintCoverageReport(
        state="ok",
        message="every resolve footprint destination is declared in version.lock",
        remediation=None,
    )

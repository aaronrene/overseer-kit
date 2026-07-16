"""Fail-closed footprint self-integrity hard gate (§KH3.4).

Detects the precise, narrow condition that motivated this module: a kit-owned
file is *declared* in ``.overseer/version.lock`` (``origin`` other than
``preserved``) but is completely *absent* from the working tree — the exact
gap that let 13 self-vendored files (``.cursor/rules/*``,
``.cursor/skills/*/SKILL.md``, ``.overseer/policy/*.yaml``,
``.overseer/STANDING-DECISIONS.reference.md``) go unrendered on this very
repo for three days without any automated check ever objecting.

This gate checks strictly against what ``version.lock`` **already records**
as installed — never against a fresh ``resolve_footprint`` re-render of the
current kit templates. That distinction matters: a kit template that has
never been through a completed ``overseer sync`` yet is a *drift* condition
(already covered by the existing ``overseer status`` drift check), not a
"declared but missing" condition — only entries the lock itself already
promised are in scope here. It also deliberately never inspects file
*content* — only existence. A kit-owned file whose content differs from its
recorded lock hash is a different, softer condition (stale hash, upstream
template change, or an unmarked customization) that stays on the existing
opt-in ``overseer status --check-footprint`` content-digest path; see
§KH3.3 for why conflating the two would risk false-closing this gate for any
consumer repo with a legitimate, not-yet-``preserved`` drift.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cli.version_lock import (
    ORIGIN_PRESERVED,
    LockError,
    VersionLock,
    entry_origin,
    lock_path,
    read_version_lock,
)

REMEDIATION = "ok sync"


@dataclass(frozen=True)
class FootprintIntegrityReport:
    """Result of a self-footprint existence probe — no shell, no content reads."""

    state: str  # ok | missing | unreadable | not_applicable
    message: str
    remediation: str | None
    missing: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.state in {"ok", "not_applicable"}


def check_footprint_integrity(
    repo_root: Path,
    *,
    lock: VersionLock | None = None,
) -> FootprintIntegrityReport:
    """Resolve a ``FootprintIntegrityReport`` for the current on-disk state.

    Pure function of ``(repo_root filesystem state, version.lock contents)``
    at call time (§KH3.8 data-integrity) — every non-``preserved`` entry
    already declared in ``version.lock`` is checked with a single
    ``Path.is_file()``; any absence fails closed as ``missing``. A lock that
    exists but cannot be parsed also fails closed as ``unreadable`` rather
    than optimistically reporting ``ok``. A repo with no ``version.lock`` at
    all has nothing declared yet, so it is vacuously ``not_applicable``
    rather than a failure.

    ``lock`` is an optional pre-computed value — callers that already loaded
    it for another purpose (``overseer status``) pass it through to avoid a
    second read (§KH3.5); callers with no prior value (``overseer review
    --freeze``, ``overseer governance-sync``) simply omit it and this
    function reads it itself.
    """
    if lock is None:
        path = lock_path(repo_root)
        if not path.is_file():
            return FootprintIntegrityReport(
                state="not_applicable",
                message="no version.lock yet — nothing declared to check",
                remediation=None,
            )
        try:
            lock = read_version_lock(path)
        except LockError as exc:
            return FootprintIntegrityReport(
                state="unreadable",
                message=f"could not read version.lock — failing closed: {exc}",
                remediation="ok init",
            )

    missing = tuple(
        sorted(
            entry.path
            for entry in lock.footprint
            if entry_origin(entry) != ORIGIN_PRESERVED
            and not (repo_root / entry.path).is_file()
        )
    )

    if missing:
        listed = ", ".join(missing)
        return FootprintIntegrityReport(
            state="missing",
            message=(
                f"{len(missing)} kit-owned footprint file(s) declared in "
                f"version.lock are absent from disk: {listed}"
            ),
            remediation=REMEDIATION,
            missing=missing,
        )

    return FootprintIntegrityReport(
        state="ok",
        message="all kit-owned footprint files declared in version.lock are present",
        remediation=None,
    )

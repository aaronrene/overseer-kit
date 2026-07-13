"""Fail-closed Muse-sync hard gate (§KH2.4).

Detects the precise, narrow condition that motivated this module: Git has
already captured a change (its working tree is clean) while Muse's tracked
snapshot still differs from the current working tree (Muse has not been
committed to since). Mid-edit work — where *both* VCS working trees are
dirty because nothing has been committed anywhere yet — is deliberately
never flagged; see §KH2.4/§KH2.6 for the frozen non-trigger rules.
"""

from __future__ import annotations

from dataclasses import dataclass

from adapters.config import OverseerConfig
from adapters.types import StatusResult

MUSE_GIT_MIRROR_REGIME = "muse+git-mirror"
REMEDIATION = 'muse code add -A && muse commit -m "<message>"'


@dataclass(frozen=True)
class MuseSyncReport:
    """Result of a Muse-sync probe — no shell, no inference from docs."""

    regime: str
    state: str  # synced | pending | not_applicable | unreadable
    message: str
    remediation: str | None

    @property
    def ok(self) -> bool:
        return self.state in {"synced", "not_applicable"}


def check_muse_sync(config: OverseerConfig, status: StatusResult) -> MuseSyncReport:
    """Resolve a ``MuseSyncReport`` from a single already-fetched ``StatusResult``.

    Pure function of ``(config.vcs.regime, status.muse_dirty, status.git_dirty)`` —
    no I/O, no additional command execution (§KH2.8 data-integrity / performance).
    """
    regime = config.vcs.regime
    if regime != MUSE_GIT_MIRROR_REGIME:
        return MuseSyncReport(
            regime=regime,
            state="not_applicable",
            message=f"{regime}: single history — no cross-VCS sync gap possible",
            remediation=None,
        )

    if status.muse_dirty is None or status.git_dirty is None:
        return MuseSyncReport(
            regime=regime,
            state="unreadable",
            message="could not determine Muse/Git working-tree state — failing closed",
            remediation="re-run overseer status once the adapter can read muse/git state",
        )

    if status.muse_dirty and not status.git_dirty:
        return MuseSyncReport(
            regime=regime,
            state="pending",
            message=(
                "Git working tree is clean but Muse has not captured the current tree — "
                "a commit landed in Git without a matching `muse commit`"
            ),
            remediation=REMEDIATION,
        )

    return MuseSyncReport(
        regime=regime,
        state="synced",
        message="Muse and Git working trees are consistent",
        remediation=None,
    )

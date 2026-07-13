"""Substrate health for Muse-backed regimes (K7 D2 / SD-14 guard)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.config import OverseerConfig

MUSE_CORE_FILES = ("HEAD", "repo.json", "config.toml")


@dataclass(frozen=True)
class SubstrateReport:
    """Result of a local substrate probe — no shell, no inference from docs."""

    regime: str
    state: str  # healthy | hollow | missing | not_applicable
    missing: tuple[str, ...]
    remediation: str | None
    message: str

    @property
    def ok(self) -> bool:
        return self.state in {"healthy", "not_applicable"}


def check_substrate(config: OverseerConfig, repo_root: Path) -> SubstrateReport:
    """Verify Muse metadata exists when config declares a Muse-backed regime."""
    regime = config.vcs.regime
    if regime == "git-only":
        return SubstrateReport(
            regime=regime,
            state="not_applicable",
            missing=(),
            remediation=None,
            message="git-only regime — Muse substrate not required",
        )

    muse_dir = repo_root / ".muse"
    if not muse_dir.is_dir():
        return _broken(
            regime,
            state="missing",
            missing=(".muse/",),
            remediation="muse init .",
            detail="config declares Muse canonical but .muse/ is absent (K7 D2 incomplete)",
        )

    missing = tuple(
        rel
        for name in MUSE_CORE_FILES
        if not (muse_dir / name).is_file()
        for rel in (f".muse/{name}",)
    )
    if missing:
        return _broken(
            regime,
            state="hollow",
            missing=missing,
            remediation="muse init --force .",
            detail=(
                "hollow .muse/ — config claims "
                f"{regime} but core Muse files missing (K7 D2 incomplete)"
            ),
        )

    return SubstrateReport(
        regime=regime,
        state="healthy",
        missing=(),
        remediation=None,
        message=f"Muse substrate healthy ({regime})",
    )


def _broken(
    regime: str,
    *,
    state: str,
    missing: tuple[str, ...],
    remediation: str,
    detail: str,
) -> SubstrateReport:
    missing_label = ", ".join(missing)
    return SubstrateReport(
        regime=regime,
        state=state,
        missing=missing,
        remediation=remediation,
        message=f"{detail}; missing: {missing_label}",
    )

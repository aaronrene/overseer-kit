"""Muse realignment guard (§5)."""

from __future__ import annotations

from adapters.base import VcsAdapter
from adapters.config import OverseerConfig
from adapters.errors import ReadError
from adapters.runner import CommandRunner, quote_arg
from tools.governance_hygiene.types import DriftReport, VerifiedReads


def plan_realign(
    config: OverseerConfig,
    adapter: VcsAdapter,
    reads: VerifiedReads,
    drift: DriftReport,
) -> tuple[bool, str]:
    """Return whether realign would run and a human-readable reason."""
    if drift.d2_anchor_vs_canonical != "drifted":
        return False, "D2 aligned — skip realign"
    if config.vcs.regime != "muse+git-mirror":
        return False, f"{config.vcs.regime}: realign no-op"
    if reads.r1_github_main_sha is None:
        return False, "missing R1 github main sha"
    if not _github_superset_of_anchor(
        adapter,
        reads.r2_anchor_sha,
        reads.r1_github_main_sha,
    ):
        return False, "R1 is not a content superset of anchor — operator required"
    return True, "D2 drift + superset precondition met"


def execute_realign_guard(
    config: OverseerConfig,
    adapter: VcsAdapter,
    reads: VerifiedReads,
    drift: DriftReport,
    *,
    dry_run: bool,
) -> tuple[str | None, str | None]:
    """
    Run §5 guard sequence.

    Returns ``(summary, error_command)`` where error_command is set on verification failure.
    """
    should_run, reason = plan_realign(config, adapter, reads, drift)
    if not should_run:
        return reason, None

    max_commits = config.thresholds.realign_max_commits
    preview = adapter.realign(dry_run=True, max_commits=max_commits)
    if isinstance(preview, ReadError):
        return None, preview.command

    if preview.would_import > max_commits:
        return (
            f"realign withheld: would_import={preview.would_import} > max={max_commits}",
            None,
        )

    if dry_run:
        return (
            f"realign planned: would_import={preview.would_import} "
            f"from {preview.from_ref} to {preview.to_ref}",
            None,
        )

    applied = adapter.realign(dry_run=False, max_commits=max_commits)
    if isinstance(applied, ReadError):
        return None, applied.command

    if not applied.applied:
        return f"realign not applied: {applied.reason}", None

    anchor = adapter.read_canonical_anchor()
    if isinstance(anchor, ReadError):
        return None, anchor.command

    muse_main = config.vcs.muse.main_branch
    head = adapter.read_head(f"muse:{muse_main}")
    if isinstance(head, ReadError):
        return None, head.command

    if anchor.anchor_sha.lower() != head.sha.lower():
        return None, "realign verification failed: anchor != muse main"

    return (
        f"realign applied: imported {applied.would_import} "
        f"from {applied.from_ref} to {applied.to_ref}",
        None,
    )


def _github_superset_of_anchor(
    adapter: VcsAdapter,
    anchor_sha: str,
    main_sha: str,
) -> bool:
    """True when ``main_sha`` contains ``anchor_sha`` (recovery precondition)."""
    if anchor_sha.lower() == main_sha.lower():
        return True
    runner = adapter.runner
    repo_root = str(adapter.repo_root)
    cmd = (
        "git merge-base --is-ancestor "
        + quote_arg(anchor_sha)
        + " "
        + quote_arg(main_sha)
    )
    result = runner.run(cmd, cwd=repo_root)
    return result.ok

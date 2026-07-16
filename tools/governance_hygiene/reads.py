"""Verified reads R1–R5 via kit adapter + gh (§2)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from adapters.base import VcsAdapter
from adapters.config import OverseerConfig
from adapters.errors import ReadError
from adapters.runner import CommandRunner
from tools.footprint_integrity import check_footprint_integrity
from tools.governance_hygiene.types import MergedPullRequest, VerifiedReads
from tools.muse_sync import check_muse_sync
from tools.substrate_health import check_substrate

GH_MERGED_LIMIT = 5


@dataclass(frozen=True)
class ReadFailure:
    """Fail-closed read error with the exact failing command."""

    command: str
    message: str
    regime: str


def perform_verified_reads(
    config: OverseerConfig,
    adapter: VcsAdapter,
    runner: CommandRunner,
    *,
    repo_root: Path | None = None,
) -> VerifiedReads | ReadFailure:
    """Execute R1–R5; stop at the first failure."""
    regime = config.vcs.regime

    if repo_root is not None:
        substrate = check_substrate(config, repo_root)
        if not substrate.ok:
            return ReadFailure(
                "substrate-health",
                substrate.message,
                regime,
            )

    status = adapter.status()
    if isinstance(status, ReadError):
        return ReadFailure(status.command, str(status), regime)

    muse_sync = check_muse_sync(config, status)
    if not muse_sync.ok:
        return ReadFailure("muse-sync", muse_sync.message, regime)

    if repo_root is not None:
        footprint_self_integrity = check_footprint_integrity(repo_root)
        if not footprint_self_integrity.ok:
            return ReadFailure(
                "footprint-self-integrity",
                footprint_self_integrity.message,
                regime,
            )

    r1_sha: str | None = None
    r1_cmd: str | None = None
    if regime in {"git-only", "muse+git-mirror"}:
        remote = config.vcs.git.remote
        main = config.vcs.git.main_branch
        r1_cmd = f"git rev-parse {remote}/{main}"
        head = adapter.read_head(f"{remote}/{main}")
        if isinstance(head, ReadError):
            return ReadFailure(head.command, str(head), regime)
        r1_sha = head.sha.lower()

    anchor = adapter.read_canonical_anchor()
    if isinstance(anchor, ReadError):
        return ReadFailure(anchor.command, str(anchor), regime)

    r3_sha: str | None = None
    r3_cmd: str | None = None
    if regime in {"muse+git-mirror", "muse-only"}:
        muse_main = config.vcs.muse.main_branch
        if not muse_main:
            return ReadFailure(
                "read_head",
                "muse.main_branch not configured",
                regime,
            )
        r3_cmd = f"muse log -1 --format=%H {muse_main}"
        head = adapter.read_head(f"muse:{muse_main}")
        if isinstance(head, ReadError):
            return ReadFailure(head.command, str(head), regime)
        r3_sha = head.sha.lower()
    elif regime == "git-only":
        r3_sha = r1_sha
        r3_cmd = r1_cmd

    merged: tuple[MergedPullRequest, ...] = ()
    if regime in {"git-only", "muse+git-mirror"}:
        gh_result = fetch_merged_prs(runner)
        if isinstance(gh_result, ReadFailure):
            return gh_result
        merged = gh_result

    return VerifiedReads(
        regime=regime,
        r1_github_main_sha=r1_sha,
        r1_command=r1_cmd,
        r2_anchor_sha=anchor.anchor_sha.lower(),
        r2_source=anchor.source,
        r3_canonical_main_sha=r3_sha,
        r3_command=r3_cmd,
        r4_merged_prs=merged,
        r5_branch=status.branch.strip(),
        r5_dirty=status.dirty,
        r5_regime=status.regime,
    )


def fetch_merged_prs(runner: CommandRunner) -> tuple[MergedPullRequest, ...] | ReadFailure:
    """R4: recent merged PRs via gh (never parse docs)."""
    command = (
        "gh pr list --state merged --limit "
        f"{GH_MERGED_LIMIT} --json number,title,mergeCommit,mergedAt"
    )
    result = runner.run(command)
    if not result.ok:
        message = result.stderr or result.stdout or "gh command failed"
        return ReadFailure(command, message, "gh")
    if not result.stdout.strip():
        return ()

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return ReadFailure(command, f"invalid json: {exc}", "gh")

    if not isinstance(payload, list):
        return ReadFailure(command, "expected JSON array", "gh")

    merged: list[MergedPullRequest] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        number = item.get("number")
        title = item.get("title")
        merge_commit = item.get("mergeCommit") or {}
        sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
        merged_at = item.get("mergedAt")
        if not isinstance(number, int) or not isinstance(title, str):
            continue
        if not isinstance(sha, str) or not sha:
            continue
        if not isinstance(merged_at, str):
            merged_at = ""
        merged.append(
            MergedPullRequest(
                number=number,
                title=title,
                merge_commit_sha=sha.lower(),
                merged_at=merged_at,
            )
        )
    return tuple(merged)

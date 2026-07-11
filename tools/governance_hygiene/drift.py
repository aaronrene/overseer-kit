"""Drift detection D1–D3 (§3)."""

from __future__ import annotations

from tools.governance_hygiene.parse import normalize_status, parse_handover_github_main_sha, parse_queue_rows, pr_matches_row
from tools.governance_hygiene.types import DriftReport, DriftState, MergedPullRequest, VerifiedReads


def detect_drift(
    reads: VerifiedReads,
    handover_text: str,
    roadmap_text: str,
) -> DriftReport:
    """Compare verified reads to doc claims; never infer VCS state from docs alone."""
    d1 = _detect_d1(reads, handover_text)
    d2 = _detect_d2(reads)
    d3 = _detect_d3(reads, roadmap_text)
    details: dict[str, str] = {}
    if d1 == "drifted":
        claimed = parse_handover_github_main_sha(handover_text)
        details["d1"] = f"claimed={claimed} actual={reads.r1_github_main_sha}"
    if d2 == "drifted":
        details["d2"] = f"anchor={reads.r2_anchor_sha} canonical={reads.r3_canonical_main_sha}"
    if d3 == "drifted":
        details["d3"] = "queue status mismatch vs merged PRs"
    return DriftReport(
        d1_handover_vs_git=d1,
        d2_anchor_vs_canonical=d2,
        d3_queue_vs_merged=d3,
        details=details,
    )


def _detect_d1(reads: VerifiedReads, handover_text: str) -> DriftState:
    if reads.regime == "muse-only":
        return "aligned"
    if reads.r1_github_main_sha is None:
        return "unreadable"
    claimed = parse_handover_github_main_sha(handover_text)
    if claimed is None:
        return "drifted"
    return "aligned" if claimed == reads.r1_github_main_sha.lower() else "drifted"


def _detect_d2(reads: VerifiedReads) -> DriftState:
    if reads.regime == "git-only":
        if reads.r3_canonical_main_sha is None:
            reads_r3 = reads.r1_github_main_sha
        else:
            reads_r3 = reads.r3_canonical_main_sha
        if reads_r3 is None:
            return "unreadable"
        return "aligned" if reads.r2_anchor_sha.lower() == reads_r3.lower() else "drifted"

    if reads.r3_canonical_main_sha is None:
        return "unreadable"
    return (
        "aligned"
        if reads.r2_anchor_sha.lower() == reads.r3_canonical_main_sha.lower()
        else "drifted"
    )


def _detect_d3(reads: VerifiedReads, roadmap_text: str) -> DriftState:
    if reads.regime == "muse-only":
        return "aligned"

    rows = parse_queue_rows(roadmap_text)
    merged = list(reads.r4_merged_prs)

    for pr in merged:
        matching = [row for row in rows if pr_matches_row(pr.title, row)]
        if not matching:
            continue
        for row in matching:
            status = normalize_status(row.status)
            if status not in {"DONE", "MERGED"}:
                return "drifted"

    for row in rows:
        status = normalize_status(row.status)
        if status != "MERGED":
            continue
        if not any(pr_matches_row(pr.title, row) for pr in merged):
            return "drifted"

    return "aligned"


def merged_prs_missing_from_done(handover_text: str, merged: tuple[MergedPullRequest, ...]) -> list[MergedPullRequest]:
    """Return merged PRs not yet mentioned in the handover done-recently block."""
    missing: list[MergedPullRequest] = []
    for pr in merged:
        if f"PR #{pr.number}" in handover_text or pr.merge_commit_sha[:7] in handover_text:
            continue
        if pr.title in handover_text:
            continue
        missing.append(pr)
    return missing

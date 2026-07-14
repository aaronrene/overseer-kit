"""Org glance discovery + repo eligibility (§HGD.4.2)."""

from __future__ import annotations

from dataclasses import dataclass

from tools.hosted_dashboard.adapters.github import GitHubAdapters, RepoMeta
from tools.hosted_dashboard.config import HostedDashboardConfig
from tools.hosted_dashboard.http_client import UpstreamError


ELIGIBILITY_ELIGIBLE = "eligible"
ELIGIBILITY_UNREADABLE = "unreadable"
ELIGIBILITY_NO_MARKER = "no_marker"


@dataclass(frozen=True)
class RepoSummary:
    owner: str
    name: str
    full_name: str
    default_branch: str
    eligibility: str
    marker_present: bool


def build_org_summary(adapters: GitHubAdapters, config: HostedDashboardConfig) -> list[RepoSummary]:
    """Return allowlisted / discovered repo summaries; empty allowlist → zero repos."""
    if not config.org_allowlist:
        return []

    candidates: list[RepoMeta] = []
    seen: set[str] = set()

    for owner, repo in config.allowlist_pairs:
        if repo is not None:
            full = f"{owner}/{repo}"
            if full in seen:
                continue
            seen.add(full)
            try:
                meta = adapters.get_repo_meta(owner, repo)
                candidates.append(meta)
            except UpstreamError:
                candidates.append(
                    RepoMeta(
                        owner=owner,
                        name=repo,
                        full_name=full,
                        default_branch="",
                        private=False,
                    )
                )
        else:
            try:
                enumerated = adapters.list_org_repos(owner)
            except UpstreamError:
                continue
            for meta in enumerated:
                if meta.full_name in seen:
                    continue
                seen.add(meta.full_name)
                candidates.append(meta)

    summaries: list[RepoSummary] = []
    for meta in candidates:
        if not meta.default_branch:
            summaries.append(
                RepoSummary(
                    owner=meta.owner,
                    name=meta.name,
                    full_name=meta.full_name,
                    default_branch="",
                    eligibility=ELIGIBILITY_UNREADABLE,
                    marker_present=False,
                )
            )
            continue
        try:
            marker = adapters.fetch_marker_summary(meta.owner, meta.name, ref=meta.default_branch)
        except UpstreamError:
            summaries.append(
                RepoSummary(
                    owner=meta.owner,
                    name=meta.name,
                    full_name=meta.full_name,
                    default_branch=meta.default_branch,
                    eligibility=ELIGIBILITY_UNREADABLE,
                    marker_present=False,
                )
            )
            continue

        # Explicit owner/repo allowlist entries appear even without marker, but
        # org-only discovery requires marker (§HGD.4.2).
        explicit = any(
            o == meta.owner and r == meta.name for o, r in config.allowlist_pairs if r is not None
        )
        if not marker.present and not explicit:
            eligibility = ELIGIBILITY_NO_MARKER
        elif not marker.present and explicit:
            # Explicit allowlist without marker: still listed, eligibility no_marker
            # so glance does not fabricate green — operator sees the gap.
            eligibility = ELIGIBILITY_NO_MARKER
        else:
            eligibility = ELIGIBILITY_ELIGIBLE

        # Filter org-discovery-only repos without marker out of the glance list.
        org_discovered = any(o == meta.owner and r is None for o, r in config.allowlist_pairs)
        if org_discovered and not explicit and not marker.present:
            continue

        summaries.append(
            RepoSummary(
                owner=meta.owner,
                name=meta.name,
                full_name=meta.full_name,
                default_branch=meta.default_branch,
                eligibility=eligibility,
                marker_present=marker.present,
            )
        )
    return summaries

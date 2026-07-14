"""Closed GET-only API handlers (§HGD.5)."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

from tools.hosted_dashboard.adapters.github import GitHubAdapters
from tools.hosted_dashboard.config import HostedDashboardConfig
from tools.hosted_dashboard.discovery import build_org_summary
from tools.hosted_dashboard.envelope import (
    ApiEnvelope,
    build_meta,
    failure,
    health_success,
    success,
)
from tools.hosted_dashboard.http_client import UpstreamError
from tools.hosted_dashboard.parsers import parse_document_derived_gates
from tools.hosted_dashboard.validators import unknown_query_keys, valid_owner_repo_segment

API_GET_ROUTES = frozenset(
    {
        "/api/health",
        "/api/org/summary",
        # repo routes matched separately
    }
)

TRACK_Q_ACT_PREFIXES = (
    "/api/review/",
    "/api/governance-sync",
    "/api/ledger/",
    "/api/honesty-status",
    "/api/init",
    "/api/sync",
)


def is_track_q_act_path(path: str) -> bool:
    return any(path == p or path.startswith(p) for p in TRACK_Q_ACT_PREFIXES)


class DashboardService:
    """Business logic for closed read surface."""

    def __init__(self, adapters: GitHubAdapters, config: HostedDashboardConfig) -> None:
        self._adapters = adapters
        self._config = config

    def health(self) -> ApiEnvelope:
        return health_success()

    def org_summary(self, query: dict[str, list[str]]) -> ApiEnvelope:
        unknown = unknown_query_keys(query)
        if unknown:
            return failure(error="unknown_query", http_status=400)
        repos = build_org_summary(self._adapters, self._config)
        result = {
            "repos": [
                {
                    "owner": r.owner,
                    "name": r.name,
                    "full_name": r.full_name,
                    "default_branch": r.default_branch,
                    "eligibility": r.eligibility,
                    "marker_present": r.marker_present,
                }
                for r in repos
            ]
        }
        return success(
            result,
            meta=build_meta(source_id="github_meta", ref="n/a"),
        )

    def roadmap(self, owner: str, repo: str, query: dict[str, list[str]]) -> ApiEnvelope:
        return self._doc_endpoint(owner, repo, query, kind="roadmap")

    def handover(self, owner: str, repo: str, query: dict[str, list[str]]) -> ApiEnvelope:
        return self._doc_endpoint(owner, repo, query, kind="handover")

    def gates(self, owner: str, repo: str, query: dict[str, list[str]]) -> ApiEnvelope:
        bad = self._validate_owner_repo_query(owner, repo, query)
        if bad is not None:
            return bad
        try:
            meta = self._adapters.get_repo_meta(owner, repo)
            marker = self._adapters.fetch_marker_summary(owner, repo, ref=meta.default_branch)
            roadmap_path, handover_path = self._adapters.doc_paths_from_marker(marker)
            roadmap_text = None
            handover_text = None
            try:
                roadmap_text = self._adapters.fetch_file(
                    owner, repo, roadmap_path, ref=meta.default_branch
                ).text
            except UpstreamError:
                pass
            try:
                handover_text = self._adapters.fetch_file(
                    owner, repo, handover_path, ref=meta.default_branch
                ).text
            except UpstreamError:
                pass
            derived = parse_document_derived_gates(
                roadmap_text=roadmap_text,
                handover_text=handover_text,
            )
            advisory = self._adapters.advisory_checks(owner, repo, ref=meta.default_branch)
            result = {
                "document_derived": {
                    "ok": derived.ok,
                    "error": derived.error,
                    "phases": derived.phases,
                    "pending_gates_excerpt": derived.pending_gates_excerpt,
                },
                "advisory_checks": advisory,
            }
            return success(
                result,
                meta=build_meta(source_id="github_contents", ref=meta.default_branch),
            )
        except UpstreamError as exc:
            return self._upstream_failure(exc)

    def config_marker(self, owner: str, repo: str, query: dict[str, list[str]]) -> ApiEnvelope:
        bad = self._validate_owner_repo_query(owner, repo, query)
        if bad is not None:
            return bad
        try:
            meta = self._adapters.get_repo_meta(owner, repo)
            marker = self._adapters.fetch_marker_summary(owner, repo, ref=meta.default_branch)
            result = {
                "present": marker.present,
                "roadmap_path": marker.roadmap_path,
                "handover_path": marker.handover_path,
                "vcs_regime": marker.vcs_regime,
            }
            # Explicitly ensure raw_text is never included.
            assert "raw_text" not in result
            return success(
                result,
                meta=build_meta(source_id="github_contents", ref=meta.default_branch),
            )
        except UpstreamError as exc:
            return self._upstream_failure(exc)

    def _doc_endpoint(
        self, owner: str, repo: str, query: dict[str, list[str]], *, kind: str
    ) -> ApiEnvelope:
        bad = self._validate_owner_repo_query(owner, repo, query)
        if bad is not None:
            return bad
        try:
            meta = self._adapters.get_repo_meta(owner, repo)
            marker = self._adapters.fetch_marker_summary(owner, repo, ref=meta.default_branch)
            roadmap_path, handover_path = self._adapters.doc_paths_from_marker(marker)
            path = roadmap_path if kind == "roadmap" else handover_path
            file = self._adapters.fetch_file(owner, repo, path, ref=meta.default_branch)
            result = {
                "path": file.path,
                "text": file.text,
                "sha256": file.sha256,
            }
            return success(
                result,
                meta=build_meta(
                    source_id=file.source_id,
                    ref=file.ref,
                    content_sha256=file.sha256,
                ),
            )
        except UpstreamError as exc:
            return self._upstream_failure(exc)

    def _validate_owner_repo_query(
        self, owner: str, repo: str, query: dict[str, list[str]]
    ) -> ApiEnvelope | None:
        if not valid_owner_repo_segment(owner) or not valid_owner_repo_segment(repo):
            return failure(error="invalid_path", http_status=400)
        unknown = unknown_query_keys(query)
        if unknown:
            return failure(error="unknown_query", http_status=400)
        return None

    @staticmethod
    def _upstream_failure(exc: UpstreamError) -> ApiEnvelope:
        if exc.token == "not_found":
            return failure(error="not_found", http_status=404)
        if exc.token == "upstream_unauthorized":
            return failure(error="upstream_unauthorized", http_status=502)
        if exc.token == "upstream_rate_limited":
            return failure(error="upstream_rate_limited", http_status=502)
        if exc.token == "upstream_host_refused":
            return failure(error="upstream_host_refused", http_status=403)
        return failure(error=exc.token, http_status=502)


def match_repo_route(path: str) -> tuple[str, str, str] | None:
    """Match ``/api/repos/{owner}/{repo}/{action}`` → (owner, repo, action)."""
    parts = path.strip("/").split("/")
    # api, repos, owner, repo, action
    if len(parts) != 5:
        return None
    if parts[0] != "api" or parts[1] != "repos":
        return None
    action = parts[4]
    if action not in {"roadmap", "handover", "gates", "config-marker"}:
        return None
    return parts[2], parts[3], action

"""GitHub Contents + meta + optional checks adapters (§HGD.4.1)."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from tools.hosted_dashboard.cache import EphemeralByteCache
from tools.hosted_dashboard.http_client import UpstreamClient, UpstreamError
from tools.hosted_dashboard.validators import (
    DEFAULT_HANDOVER_PATH,
    DEFAULT_ORG_ENUMERATION_CAP,
    DEFAULT_ROADMAP_PATH,
    MARKER_PATH,
)

GITHUB_API = "https://api.github.com"


@dataclass(frozen=True)
class RepoMeta:
    """Repository metadata from ``github_meta``."""

    owner: str
    name: str
    full_name: str
    default_branch: str
    private: bool


@dataclass(frozen=True)
class FileContent:
    """Fetched file bytes with digest."""

    path: str
    text: str
    raw: bytes
    sha256: str
    ref: str
    source_id: str


@dataclass(frozen=True)
class MarkerSummary:
    """Redacted marker parse (§HGD.5.7)."""

    present: bool
    roadmap_path: str | None
    handover_path: str | None
    vcs_regime: str | None


class GitHubAdapters:
    """Baseline ``github_contents`` + ``github_meta`` (+ optional checks)."""

    def __init__(
        self,
        client: UpstreamClient,
        *,
        cache: EphemeralByteCache | None = None,
        checks_advisory: bool = False,
        enumeration_cap: int = DEFAULT_ORG_ENUMERATION_CAP,
        max_doc_bytes: int = 2_000_000,
    ) -> None:
        self._client = client
        self._cache = cache or EphemeralByteCache()
        self._checks_advisory = checks_advisory
        self._enumeration_cap = enumeration_cap
        self._max_doc_bytes = max_doc_bytes

    @property
    def cache(self) -> EphemeralByteCache:
        return self._cache

    def get_repo_meta(self, owner: str, repo: str) -> RepoMeta:
        data = self._client.get_json(f"{GITHUB_API}/repos/{quote(owner)}/{quote(repo)}")
        if not isinstance(data, dict):
            raise UpstreamError("upstream_error", detail="invalid repo meta")
        default_branch = data.get("default_branch")
        if not isinstance(default_branch, str) or not default_branch.strip():
            raise UpstreamError("not_found", detail="missing default_branch")
        return RepoMeta(
            owner=str(data.get("owner", {}).get("login", owner)),
            name=str(data.get("name", repo)),
            full_name=str(data.get("full_name", f"{owner}/{repo}")),
            default_branch=default_branch.strip(),
            private=bool(data.get("private", False)),
        )

    def list_org_repos(self, owner: str) -> list[RepoMeta]:
        """Enumerate repos under ``owner`` capped at ``enumeration_cap``."""
        out: list[RepoMeta] = []
        page = 1
        while len(out) < self._enumeration_cap:
            url = (
                f"{GITHUB_API}/orgs/{quote(owner)}/repos"
                f"?per_page=100&page={page}&type=all"
            )
            try:
                data = self._client.get_json(url)
            except UpstreamError:
                # Fallback to user repos listing when orgs endpoint fails.
                url = (
                    f"{GITHUB_API}/users/{quote(owner)}/repos"
                    f"?per_page=100&page={page}&type=all"
                )
                data = self._client.get_json(url)
            if not isinstance(data, list) or not data:
                break
            for item in data:
                if len(out) >= self._enumeration_cap:
                    break
                if not isinstance(item, dict):
                    continue
                default_branch = item.get("default_branch")
                if not isinstance(default_branch, str) or not default_branch.strip():
                    continue
                out.append(
                    RepoMeta(
                        owner=str(item.get("owner", {}).get("login", owner)),
                        name=str(item.get("name", "")),
                        full_name=str(item.get("full_name", "")),
                        default_branch=default_branch.strip(),
                        private=bool(item.get("private", False)),
                    )
                )
            if len(data) < 100:
                break
            page += 1
        return out

    def fetch_file(self, owner: str, repo: str, path: str, *, ref: str) -> FileContent:
        cache_key = f"gh:{owner}/{repo}:{ref}:{path}"
        cached = self._cache.get(cache_key)
        if cached is not None and isinstance(cached.payload, FileContent):
            return cached.payload

        url = (
            f"{GITHUB_API}/repos/{quote(owner)}/{quote(repo)}/contents/"
            f"{quote(path, safe='/')}?ref={quote(ref)}"
        )
        # Prefer raw accept to avoid base64 decode complexity when available.
        try:
            raw = self._client.get_bytes(url, accept="application/vnd.github.raw")
        except UpstreamError:
            data = self._client.get_json(url)
            if not isinstance(data, dict):
                raise UpstreamError("upstream_error", detail="invalid contents")
            encoding = data.get("encoding")
            content = data.get("content")
            if encoding == "base64" and isinstance(content, str):
                raw = base64.b64decode(content)
            elif isinstance(content, str):
                raw = content.encode("utf-8")
            else:
                raise UpstreamError("not_found", detail="empty contents")

        if len(raw) > self._max_doc_bytes:
            raw = raw[: self._max_doc_bytes]
        text = raw.decode("utf-8", errors="replace")
        entry = self._cache.put(cache_key, raw)
        result = FileContent(
            path=path,
            text=text,
            raw=raw,
            sha256=entry.sha256,
            ref=ref,
            source_id="github_contents",
        )
        self._cache.put(cache_key, raw, payload=result)
        return result

    def fetch_marker_summary(self, owner: str, repo: str, *, ref: str) -> MarkerSummary:
        try:
            file = self.fetch_file(owner, repo, MARKER_PATH, ref=ref)
        except UpstreamError as exc:
            if exc.token == "not_found":
                return MarkerSummary(
                    present=False,
                    roadmap_path=None,
                    handover_path=None,
                    vcs_regime=None,
                )
            raise
        return parse_marker_yaml(file.text)

    def doc_paths_from_marker(self, marker: MarkerSummary) -> tuple[str, str]:
        roadmap = marker.roadmap_path or DEFAULT_ROADMAP_PATH
        handover = marker.handover_path or DEFAULT_HANDOVER_PATH
        return roadmap, handover

    def advisory_checks(self, owner: str, repo: str, *, ref: str) -> dict[str, Any] | None:
        if not self._checks_advisory:
            return None
        url = f"{GITHUB_API}/repos/{quote(owner)}/{quote(repo)}/commits/{quote(ref)}/check-runs"
        try:
            data = self._client.get_json(url)
        except UpstreamError as exc:
            return {
                "ok": False,
                "label": "Advisory — not kit hard gates",
                "items": [],
                "error": exc.token,
            }
        items: list[dict[str, str]] = []
        check_runs = data.get("check_runs") if isinstance(data, dict) else None
        if isinstance(check_runs, list):
            for run in check_runs:
                if not isinstance(run, dict):
                    continue
                name = str(run.get("name") or "check")
                conclusion = str(run.get("conclusion") or run.get("status") or "unknown")
                items.append({"name": name, "conclusion": conclusion})
        return {
            "ok": True,
            "label": "Advisory — not kit hard gates",
            "items": items,
        }


def parse_marker_yaml(text: str) -> MarkerSummary:
    """Parse living-doc paths + regime from marker YAML; never returns raw secrets."""
    try:
        import yaml

        data = yaml.safe_load(text)
    except Exception:
        return MarkerSummary(present=True, roadmap_path=None, handover_path=None, vcs_regime=None)

    if not isinstance(data, dict):
        return MarkerSummary(present=True, roadmap_path=None, handover_path=None, vcs_regime=None)

    docs = data.get("docs") if isinstance(data.get("docs"), dict) else {}
    roadmap = docs.get("roadmap") if isinstance(docs, dict) else None
    handover = docs.get("handover") if isinstance(docs, dict) else None
    # Paths in config are often filenames under docs/; compose defaults.
    roadmap_path = _compose_doc_path(roadmap)
    handover_path = _compose_doc_path(handover)

    vcs = data.get("vcs") if isinstance(data.get("vcs"), dict) else {}
    regime = vcs.get("regime") if isinstance(vcs, dict) else None
    regime_str = regime if isinstance(regime, str) else None

    return MarkerSummary(
        present=True,
        roadmap_path=roadmap_path,
        handover_path=handover_path,
        vcs_regime=regime_str,
    )


def _compose_doc_path(name: Any) -> str | None:
    if not isinstance(name, str) or not name.strip():
        return None
    text = name.strip().lstrip("./")
    if text.startswith("docs/"):
        return text
    if "/" in text:
        return text
    return f"docs/{text}"

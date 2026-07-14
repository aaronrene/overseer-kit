"""Fixture helpers for hosted governance dashboard tests (§HGD.12)."""

from __future__ import annotations

import base64
import json
import socket
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from tools.hosted_dashboard.adapters.github import GitHubAdapters
from tools.hosted_dashboard.auth import generate_viewer_token
from tools.hosted_dashboard.config import HostedDashboardConfig, parse_hosted_dashboard_config
from tools.hosted_dashboard.handlers import DashboardService
from tools.hosted_dashboard.http_client import UpstreamClient, UpstreamResponse
from tools.hosted_dashboard.server import HostedServerConfig, HostedServerHandle, start_hosted_server

MARKER_YAML = """\
overseer_config_version: 1
repo:
  name: demo
  root_relative_docs: docs
vcs:
  regime: git-only
  canonical: git
  git:
    remote: origin
    main_branch: main
    mirror_branch: null
    feature_branch_pattern: "feat/*"
  muse:
    staging_remote: null
    main_branch: null
docs:
  handover: OVERSEER-HANDOVER.md
  roadmap: ROADMAP.md
  coordination: null
  standing_decisions: STANDING-DECISIONS.md
  handover_title: Handover
  roadmap_title: Roadmap
thresholds:
  realign_max_commits: 5
  drift_warn_only: true
freeze_contract:
  enabled: true
  reviewer:
    mode: agent
    model: thinking-high
    provider: local
    fallback: human
  human_escalation: [security, irreversible, real_money, gates_tier3]
"""

ROADMAP_MD = """\
# Roadmap fixture

| Phase | Model | Status | Notes |
| --- | --- | --- | --- |
| **Alpha** | Auto | **DONE** | shipped |
| **Beta** | Thinking | **WIP** | in progress |
| **Gamma** | Auto | **TODO** | pending |
"""

HANDOVER_MD = """\
# Handover fixture

## Pending gates

- freeze-review for Gamma still open
- build-verification not yet run

## Snapshot
ok
"""


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class FixtureUpstream:
    """In-memory GitHub Contents-shaped fixture (no real network)."""

    def __init__(self) -> None:
        self.files: dict[tuple[str, str, str, str], bytes] = {}
        self.repos: dict[tuple[str, str], dict[str, Any]] = {}
        self.org_repos: dict[str, list[dict[str, Any]]] = {}
        self.calls: list[tuple[str, str]] = []
        self.force_status: dict[str, int] = {}

    def put_repo(self, owner: str, name: str, *, default_branch: str = "main", private: bool = False) -> None:
        self.repos[(owner, name)] = {
            "name": name,
            "full_name": f"{owner}/{name}",
            "default_branch": default_branch,
            "private": private,
            "owner": {"login": owner},
        }
        self.org_repos.setdefault(owner, [])
        entry = self.repos[(owner, name)]
        if entry not in self.org_repos[owner]:
            self.org_repos[owner].append(entry)

    def put_file(self, owner: str, repo: str, path: str, content: str | bytes, *, ref: str = "main") -> None:
        raw = content.encode("utf-8") if isinstance(content, str) else content
        self.files[(owner, repo, ref, path)] = raw

    def seed_kit_repo(self, owner: str = "acme", repo: str = "kit-demo") -> None:
        self.put_repo(owner, repo)
        self.put_file(owner, repo, ".overseer/config.yaml", MARKER_YAML)
        self.put_file(owner, repo, "docs/ROADMAP.md", ROADMAP_MD)
        self.put_file(owner, repo, "docs/OVERSEER-HANDOVER.md", HANDOVER_MD)

    def transport(self, method: str, url: str, headers: dict[str, str], timeout: float) -> UpstreamResponse:
        self.calls.append((method, url))
        if method not in {"GET", "HEAD"}:
            raise AssertionError(f"write verb attempted: {method}")
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if host not in {"api.github.com", "raw.githubusercontent.com"}:
            # Host allowlist in client should have refused before transport; if not, 403 token path.
            return UpstreamResponse(status=403, headers={}, body=b"host refused")

        path = parsed.path
        qs = parse_qs(parsed.query)

        # Force status override by path prefix
        for prefix, status in self.force_status.items():
            if prefix in url:
                return UpstreamResponse(status=status, headers={}, body=b"forced")

        # /repos/{owner}/{repo}
        parts = [p for p in path.split("/") if p]
        if len(parts) == 3 and parts[0] == "repos":
            owner, repo = parts[1], parts[2]
            meta = self.repos.get((owner, repo))
            if meta is None:
                return UpstreamResponse(status=404, headers={}, body=b"{}")
            body = json.dumps(meta).encode("utf-8")
            return UpstreamResponse(status=200, headers={"content-type": "application/json"}, body=body)

        # /repos/{o}/{r}/contents/{path}
        if len(parts) >= 4 and parts[0] == "repos" and parts[3] == "contents":
            owner, repo = parts[1], parts[2]
            file_path = "/".join(parts[4:])
            ref = (qs.get("ref") or ["main"])[0]
            raw = self.files.get((owner, repo, ref, file_path))
            if raw is None:
                return UpstreamResponse(status=404, headers={}, body=b"{}")
            accept = headers.get("Accept", "")
            if "raw" in accept:
                return UpstreamResponse(status=200, headers={}, body=raw if method == "GET" else b"")
            payload = {
                "encoding": "base64",
                "content": base64.b64encode(raw).decode("ascii"),
                "path": file_path,
            }
            return UpstreamResponse(
                status=200,
                headers={"content-type": "application/json"},
                body=json.dumps(payload).encode("utf-8") if method == "GET" else b"",
            )

        # /orgs/{owner}/repos or /users/{owner}/repos
        if len(parts) == 3 and parts[0] in {"orgs", "users"} and parts[2] == "repos":
            owner = parts[1]
            data = self.org_repos.get(owner, [])
            return UpstreamResponse(
                status=200,
                headers={"content-type": "application/json"},
                body=json.dumps(data).encode("utf-8"),
            )

        # check-runs
        if len(parts) >= 5 and parts[3] == "commits" and parts[-1] == "check-runs":
            payload = {
                "check_runs": [
                    {"name": "ci", "conclusion": "success"},
                ]
            }
            return UpstreamResponse(
                status=200,
                headers={"content-type": "application/json"},
                body=json.dumps(payload).encode("utf-8"),
            )

        return UpstreamResponse(status=404, headers={}, body=b"{}")


class HostedHttpClient:
    """Minimal HTTP client for hosted dashboard tests."""

    def __init__(self, base_url: str, viewer_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.viewer_token = viewer_token

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        origin: str | None = None,
        auth: bool = True,
    ) -> tuple[int, dict[str, Any] | str]:
        url = f"{self.base_url}{path}"
        req_headers = dict(headers or {})
        if auth:
            req_headers.setdefault("Authorization", f"Bearer {self.viewer_token}")
        if origin is not None:
            req_headers["Origin"] = origin
        request = urllib.request.Request(url, method=method, headers=req_headers)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                raw = response.read().decode("utf-8")
                try:
                    return response.status, json.loads(raw)
                except json.JSONDecodeError:
                    return response.status, raw
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                return exc.code, json.loads(raw)
            except json.JSONDecodeError:
                return exc.code, raw

    def get(self, path: str, **kwargs: Any) -> tuple[int, dict[str, Any] | str]:
        return self.request("GET", path, **kwargs)


def start_test_hosted(
    *,
    upstream: FixtureUpstream | None = None,
    config: HostedDashboardConfig | None = None,
    viewer_token: str | None = None,
    port: int | None = None,
    write_scope_refused: bool = False,
    cors_origins: tuple[str, ...] | None = None,
) -> tuple[HostedServerHandle, HostedHttpClient, FixtureUpstream]:
    """Start hosted dashboard against fixture upstream."""
    fixture = upstream or FixtureUpstream()
    if not fixture.repos:
        fixture.seed_kit_repo()

    dash = config
    if dash is None:
        raw = {
            "enabled": True,
            "allow_non_loopback": False,
            "cors_origins": list(cors_origins or ()),
            "org_allowlist": ["acme/kit-demo"],
            "sources": {
                "github_contents": True,
                "github_meta": True,
                "github_checks_advisory": False,
                "musehub_read": False,
            },
        }
        dash = parse_hosted_dashboard_config(raw)

    token = viewer_token or generate_viewer_token()
    client = UpstreamClient(token="test-upstream", transport=fixture.transport)
    adapters = GitHubAdapters(
        client,
        checks_advisory=dash.sources.github_checks_advisory,
        enumeration_cap=dash.enumeration_cap,
        max_doc_bytes=dash.max_doc_bytes,
    )
    service = DashboardService(adapters, dash)
    chosen = port or free_port()
    server_config = HostedServerConfig(
        bind="127.0.0.1",
        port=chosen,
        viewer_token=token,
        upstream_token="test-upstream",
        dashboard=dash,
        service=service,
        require_loopback_peer=True,
        write_scope_refused=write_scope_refused,
    )
    handle = start_hosted_server(server_config)
    http = HostedHttpClient(handle.base_url, token)
    return handle, http, fixture


def write_hosted_config(path: Path, block: dict[str, Any]) -> Path:
    """Write a minimal overseer config with hosted_dashboard block for CLI tests."""
    from tests.support import FIXTURES
    import yaml
    import shutil

    base = yaml.safe_load((FIXTURES / "config-git-only.yaml").read_text(encoding="utf-8"))
    base["hosted_dashboard"] = block
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
    return path

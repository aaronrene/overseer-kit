"""GET/HEAD-only upstream HTTP client with host allowlist (§HGD.6.6, §HGD.11)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlparse

from tools.hosted_dashboard.hosts import url_host_allowed

ALLOWED_METHODS = frozenset({"GET", "HEAD"})


class UpstreamError(Exception):
    """Upstream fetch failure with frozen error token."""

    def __init__(self, token: str, *, status: int | None = None, detail: str | None = None) -> None:
        super().__init__(token)
        self.token = token
        self.status = status
        self.detail = detail


@dataclass(frozen=True)
class UpstreamResponse:
    """Raw upstream response."""

    status: int
    headers: dict[str, str]
    body: bytes


Transport = Callable[[str, str, dict[str, str], float], UpstreamResponse]


def _default_transport(method: str, url: str, headers: dict[str, str], timeout: float) -> UpstreamResponse:
    if method not in ALLOWED_METHODS:
        raise UpstreamError("method_refused", detail=f"method {method} not allowed")
    request = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read() if method == "GET" else b""
            return UpstreamResponse(
                status=int(response.status),
                headers={k.lower(): v for k, v in response.headers.items()},
                body=body,
            )
    except urllib.error.HTTPError as exc:
        body = exc.read() if method == "GET" else b""
        return UpstreamResponse(
            status=int(exc.code),
            headers={k.lower(): v for k, v in exc.headers.items()} if exc.headers else {},
            body=body,
        )
    except urllib.error.URLError as exc:
        raise UpstreamError("upstream_unreachable", detail=str(exc.reason)) from exc


class UpstreamClient:
    """Host-allowlisted GET/HEAD client for GitHub/MuseHub read APIs."""

    def __init__(
        self,
        *,
        token: str | None,
        extra_allowed_hosts: frozenset[str] | None = None,
        transport: Transport | None = None,
        timeout: float = 15.0,
        user_agent: str = "overseer-hosted-dashboard/0.1",
    ) -> None:
        self._token = token
        self._extra = extra_allowed_hosts or frozenset()
        self._transport = transport or _default_transport
        self._timeout = timeout
        self._user_agent = user_agent

    def request(self, method: str, url: str, *, accept: str = "application/json") -> UpstreamResponse:
        method_upper = method.upper()
        if method_upper not in ALLOWED_METHODS:
            raise UpstreamError("method_refused", detail=f"method {method} not allowed")
        if not url_host_allowed(url, extra_allowed=self._extra):
            raise UpstreamError("upstream_host_refused")
        headers = {
            "Accept": accept,
            "User-Agent": self._user_agent,
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return self._transport(method_upper, url, headers, self._timeout)

    def get_json(self, url: str) -> Any:
        """GET JSON; map upstream status codes to frozen error tokens."""
        response = self.request("GET", url, accept="application/vnd.github+json")
        return self._map_response(response, expect_json=True)

    def get_bytes(self, url: str, *, accept: str = "application/vnd.github.raw") -> bytes:
        """GET raw bytes for Contents/raw endpoints."""
        response = self.request("GET", url, accept=accept)
        return self._map_response(response, expect_json=False)  # type: ignore[return-value]

    def _map_response(self, response: UpstreamResponse, *, expect_json: bool) -> Any:
        if response.status == 404:
            raise UpstreamError("not_found", status=404)
        if response.status in {401, 403}:
            # Distinguishing rate limit vs auth: GitHub sends X-RateLimit-Remaining: 0
            remaining = response.headers.get("x-ratelimit-remaining")
            if remaining == "0" or response.status == 403 and "rate limit" in response.body.decode(
                "utf-8", errors="replace"
            ).lower():
                raise UpstreamError("upstream_rate_limited", status=response.status)
            raise UpstreamError("upstream_unauthorized", status=response.status)
        if response.status == 429:
            raise UpstreamError("upstream_rate_limited", status=429)
        if response.status < 200 or response.status >= 300:
            raise UpstreamError("upstream_error", status=response.status)
        if expect_json:
            try:
                return json.loads(response.body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise UpstreamError("upstream_error", detail="invalid json") from exc
        return response.body

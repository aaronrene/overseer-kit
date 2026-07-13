"""HTTP transport and headless review API client (§K5.8 / K11)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from urllib.parse import urljoin

from tools.freeze_reviewer.providers.api_prompt import (
    build_review_request_body,
    serialize_review_request,
)
from tools.freeze_reviewer.providers.api_response import (
    ProviderReviewError,
    parse_review_response,
)
from tools.freeze_reviewer.providers.model_hint import resolve_model_hint
from tools.freeze_reviewer.types import ChecklistItem, Finding, ReviewerSettings

DEFAULT_API_KEY_VAR = "OVERSEER_REVIEW_API_KEY"
DEFAULT_API_URL_VAR = "OVERSEER_REVIEW_API_URL"
HEALTH_PATH = "/health"
REVIEW_PATH = "/review"
DEFAULT_TIMEOUT_SECONDS = 30.0


class ProviderTransportError(Exception):
    """Raised when the HTTP transport cannot complete a request."""


class HttpTransport(Protocol):
    """Injectable HTTP transport for tests (no network in CI)."""

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> tuple[int, bytes]:
        """Return HTTP status code and response body bytes."""


@dataclass
class UrllibTransport:
    """Production HTTP transport using stdlib urllib."""

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> tuple[int, bytes]:
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            raise ProviderTransportError(str(reason)) from exc


@dataclass
class ReviewApiConfig:
    """Resolved API credentials and endpoint (never logged)."""

    api_key: str
    base_url: str


@dataclass
class ReviewApiClient:
    """Headless freeze-review HTTP client."""

    kit_root: Path | None = None
    transport: HttpTransport = field(default_factory=UrllibTransport)
    api_key_var: str = DEFAULT_API_KEY_VAR
    url_var: str = DEFAULT_API_URL_VAR
    timeout: float = DEFAULT_TIMEOUT_SECONDS
    last_request_url: str | None = field(default=None, init=False)
    last_request_body: bytes | None = field(default=None, init=False)

    def resolve_config(self) -> ReviewApiConfig | None:
        """Load API config from environment; return None when incomplete."""
        api_key = os.environ.get(self.api_key_var, "").strip()
        if not api_key:
            return None
        base_url = os.environ.get(self.url_var, "").strip().rstrip("/")
        if not base_url:
            return None
        return ReviewApiConfig(api_key=api_key, base_url=base_url)

    def reachable(self) -> tuple[bool, str | None]:
        """Probe API health without sending artifact content (§K5.8)."""
        config = self.resolve_config()
        if config is None:
            if not os.environ.get(self.api_key_var, "").strip():
                return False, "missing API credentials"
            return False, "missing API base URL"
        url = urljoin(config.base_url + "/", HEALTH_PATH.lstrip("/"))
        headers = {"Authorization": f"Bearer {config.api_key}", "Accept": "application/json"}
        try:
            status, _body = self.transport.request(
                method="GET",
                url=url,
                headers=headers,
                timeout=self.timeout,
            )
        except ProviderTransportError as exc:
            return False, f"API transport error: {exc}"
        if 200 <= status < 300:
            return True, None
        return False, f"API health check failed with status {status}"

    def review(
        self,
        *,
        artifact_text: str,
        artifact_path: str,
        checklist: list[ChecklistItem],
        reviewer: ReviewerSettings,
    ) -> list[Finding]:
        """POST artifact to the review API and parse findings."""
        config = self.resolve_config()
        if config is None:
            raise ProviderReviewError("API credentials or base URL not configured")
        if not reviewer.model:
            raise ProviderReviewError("reviewer model label is required for API review")

        model_hint = resolve_model_hint(reviewer.model, kit_root=self.kit_root)
        body = build_review_request_body(
            artifact_text=artifact_text,
            artifact_path=artifact_path,
            checklist=checklist,
            model_label=reviewer.model,
            model_hint=model_hint,
        )
        payload = serialize_review_request(body)
        url = urljoin(config.base_url + "/", REVIEW_PATH.lstrip("/"))
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.last_request_url = url
        self.last_request_body = payload
        try:
            status, response_body = self.transport.request(
                method="POST",
                url=url,
                headers=headers,
                body=payload,
                timeout=self.timeout,
            )
        except ProviderTransportError as exc:
            raise ProviderReviewError(f"API transport error: {exc}") from exc
        if status < 200 or status >= 300:
            snippet = _safe_error_snippet(response_body)
            raise ProviderReviewError(f"review API failed with status {status}: {snippet}")
        return parse_review_response(response_body, default_path=artifact_path)


def _safe_error_snippet(body: bytes, limit: int = 120) -> str:
    """Return a short non-secret error snippet for provider_cause."""
    try:
        text = body.decode("utf-8", errors="replace").strip()
    except Exception:
        return "unreadable response body"
    if not text:
        return "empty response body"
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            message = parsed.get("error") or parsed.get("message")
            if isinstance(message, str) and message.strip():
                text = message.strip()
    except json.JSONDecodeError:
        pass
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text

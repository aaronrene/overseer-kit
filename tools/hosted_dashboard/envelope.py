"""JSON response envelope for hosted-dashboard ``api/*`` (§HGD.5.3)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 with ``Z`` suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class ApiEnvelope:
    """Standard hosted-dashboard API response wrapper."""

    ok: bool
    result: Any
    error: str | None = None
    http_status: int = 200
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": self.ok,
            "result": self.result,
        }
        if self.error is not None:
            payload["error"] = self.error
        if self.meta is not None:
            payload["meta"] = self.meta
        return payload

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True).encode("utf-8")


def build_meta(
    *,
    source_id: str,
    ref: str,
    content_sha256: str | None = None,
    fetched_at: str | None = None,
) -> dict[str, Any]:
    """Build the frozen ``meta`` object; ``authoritative_workflow`` is always ``local``."""
    meta: dict[str, Any] = {
        "source_id": source_id,
        "ref": ref,
        "fetched_at": fetched_at or utc_now_iso(),
        "authoritative_workflow": "local",
    }
    if content_sha256 is not None:
        meta["content_sha256"] = content_sha256
    return meta


def success(result: Any, *, meta: dict[str, Any], http_status: int = 200) -> ApiEnvelope:
    """Successful response with required meta."""
    return ApiEnvelope(ok=True, result=result, error=None, http_status=http_status, meta=meta)


def failure(
    *,
    error: str,
    http_status: int,
    result: Any = None,
    meta: dict[str, Any] | None = None,
) -> ApiEnvelope:
    """Failed response with error token."""
    return ApiEnvelope(ok=False, result=result, error=error, http_status=http_status, meta=meta)


def health_success() -> ApiEnvelope:
    """``api/health`` body (§HGD.5.4)."""
    return ApiEnvelope(
        ok=True,
        result={"status": "ok", "mode": "hosted-read-only"},
        error=None,
        http_status=200,
        meta=build_meta(source_id="github_meta", ref="n/a", content_sha256=None),
    )

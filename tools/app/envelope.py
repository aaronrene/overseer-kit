"""JSON response envelope for ``api/*`` routes (§Q0.10.2)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApiEnvelope:
    """Standard API response wrapper."""

    ok: bool
    exit_code: int | None
    error: str | None
    result: Any
    http_status: int = 200

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": self.ok,
            "exit_code": self.exit_code,
            "error": self.error,
            "result": self.result,
        }
        return payload

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True).encode("utf-8")


def auth_refusal(*, http_status: int, error: str) -> ApiEnvelope:
    """Build an adapter refusal envelope without a CLI exit code."""
    return ApiEnvelope(ok=False, exit_code=None, error=error, result=None, http_status=http_status)


def engine_success(result: Any, *, exit_code: int = 0) -> ApiEnvelope:
    """Build a successful engine response."""
    return ApiEnvelope(ok=exit_code == 0, exit_code=exit_code, error=None, result=result, http_status=200)


def engine_failure(*, exit_code: int, error: str | None, result: Any = None) -> ApiEnvelope:
    """Build a failed engine response with CLI parity exit code."""
    return ApiEnvelope(ok=False, exit_code=exit_code, error=error, result=result, http_status=200)


def bad_request(error: str = "bad_request") -> ApiEnvelope:
    """Reject malformed API input before invoking the engine."""
    return ApiEnvelope(ok=False, exit_code=None, error=error, result=None, http_status=400)

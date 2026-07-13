"""Capture JSON emitted by CLI commands for HTTP handlers."""

from __future__ import annotations

from typing import Any

from cli.output import OutputContext


class CapturingOutputContext(OutputContext):
    """Output context that records the last JSON payload instead of printing it."""

    def __init__(self) -> None:
        super().__init__(json_mode=True, quiet=True)
        self.json_payload: dict[str, Any] | None = None

    def emit_json(self, payload: dict[str, Any]) -> None:
        self.json_payload = payload

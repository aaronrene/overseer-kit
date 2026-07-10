"""CLI output formatting and reporting."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OutputContext:
    """Stdout/stderr discipline for human and JSON modes."""

    json_mode: bool = False
    quiet: bool = False
    verbose: bool = False
    no_color: bool = False

    def __post_init__(self) -> None:
        if not self.no_color and not sys.stdout.isatty():
            self.no_color = True

    def emit(self, message: str) -> None:
        """Print a human message to stdout unless quiet/json."""
        if self.json_mode or self.quiet:
            return
        print(message)

    def emit_json(self, payload: dict[str, Any]) -> None:
        """Print exactly one JSON object to stdout."""
        print(json.dumps(payload, indent=2, sort_keys=True))

    def warn(self, message: str) -> None:
        """Print a warning to stderr."""
        print(message, file=sys.stderr)

    def error(self, message: str) -> None:
        """Print an error to stderr."""
        print(message, file=sys.stderr)

    def verbose_msg(self, message: str) -> None:
        """Print diagnostic detail to stderr when verbose."""
        if self.verbose:
            print(message, file=sys.stderr)


@dataclass
class CommandReport:
    """Mutable report payload shared across command phases."""

    data: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def to_payload(self) -> dict[str, Any]:
        payload = dict(self.data)
        payload["warnings"] = list(self.warnings)
        return payload

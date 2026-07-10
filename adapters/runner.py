"""Injectable command runner for VCS subprocess calls."""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


class CommandRunner(Protocol):
    """Protocol for executing shell commands (real or mocked)."""

    def run(self, command: str, *, cwd: str | None = None) -> CommandResult:
        """Execute ``command`` and return stdout/stderr/exit_code."""


@dataclass
class SubprocessRunner:
    """Production runner using ``subprocess``."""

    def run(self, command: str, *, cwd: str | None = None) -> CommandResult:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        return CommandResult(
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
            exit_code=completed.returncode,
        )


@dataclass
class RecordingRunner:
    """Test runner that records commands and returns scripted responses."""

    responses: dict[str, CommandResult]
    calls: list[tuple[str, str | None]]

    def run(self, command: str, *, cwd: str | None = None) -> CommandResult:
        self.calls.append((command, cwd))
        if command in self.responses:
            return self.responses[command]
        for pattern, result in self.responses.items():
            if pattern in command:
                return result
        return CommandResult(stdout="", stderr="unmocked command", exit_code=127)


def quote_arg(value: str) -> str:
    """Shell-quote a single argument."""
    return shlex.quote(value)

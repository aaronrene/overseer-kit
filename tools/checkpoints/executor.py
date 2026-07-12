"""Script execution without shell (§K9.5)."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExecResult:
    """Result of executing a verify script."""

    stdout: bytes
    stderr: bytes
    exit_code: int


class ScriptExecutor(Protocol):
    """Protocol for argv-list script invocation."""

    def exec_argv(
        self,
        argv: list[str],
        *,
        cwd: str,
        env: dict[str, str] | None = None,
    ) -> ExecResult:
        """Run ``argv[0]`` with remaining args; no shell."""


@dataclass
class SubprocessScriptExecutor:
    """Production executor using ``subprocess.run`` with argv list."""

    def exec_argv(
        self,
        argv: list[str],
        *,
        cwd: str,
        env: dict[str, str] | None = None,
    ) -> ExecResult:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=merged_env,
            capture_output=True,
        )
        return ExecResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        )


@dataclass
class RecordingScriptExecutor:
    """Test executor recording argv invocations."""

    responses: dict[tuple[str, ...], ExecResult]
    calls: list[tuple[list[str], str, dict[str, str] | None]]

    def exec_argv(
        self,
        argv: list[str],
        *,
        cwd: str,
        env: dict[str, str] | None = None,
    ) -> ExecResult:
        self.calls.append((list(argv), cwd, env))
        key = tuple(argv)
        if key in self.responses:
            return self.responses[key]
        script = argv[0] if argv else ""
        for pattern, result in self.responses.items():
            if pattern and pattern[0] == script:
                return result
        return ExecResult(stdout=b"", stderr=b"unmocked script", exit_code=127)

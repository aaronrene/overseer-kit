"""Shared CLI runtime context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from adapters.runner import CommandRunner, SubprocessRunner
from cli.kit_root import kit_root
from cli.output import OutputContext


@dataclass
class CliContext:
    """Injectable runtime dependencies for commands and tests."""

    kit: Path
    runner: CommandRunner
    output: OutputContext
    cwd: Path

    @classmethod
    def create(
        cls,
        *,
        output: OutputContext | None = None,
        runner: CommandRunner | None = None,
        cwd: Path | None = None,
        kit: Path | None = None,
    ) -> CliContext:
        return cls(
            kit=kit or kit_root(),
            runner=runner or SubprocessRunner(),
            output=output or OutputContext(),
            cwd=cwd or Path.cwd(),
        )

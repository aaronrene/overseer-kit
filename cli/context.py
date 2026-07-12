"""Shared CLI runtime context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from adapters.runner import CommandRunner, SubprocessRunner
from cli.kit_root import kit_root
from cli.output import OutputContext
from tools.checkpoints.executor import ScriptExecutor
from tools.freeze_reviewer.providers.base import ReviewProvider


@dataclass
class CliContext:
    """Injectable runtime dependencies for commands and tests."""

    kit: Path
    runner: CommandRunner
    output: OutputContext
    cwd: Path
    review_provider_factory: Callable[[str], ReviewProvider] | None = None
    script_executor: ScriptExecutor | None = None

    @classmethod
    def create(
        cls,
        *,
        output: OutputContext | None = None,
        runner: CommandRunner | None = None,
        cwd: Path | None = None,
        kit: Path | None = None,
        review_provider_factory: Callable[[str], ReviewProvider] | None = None,
        script_executor: ScriptExecutor | None = None,
    ) -> CliContext:
        return cls(
            kit=kit or kit_root(),
            runner=runner or SubprocessRunner(),
            output=output or OutputContext(),
            cwd=cwd or Path.cwd(),
            review_provider_factory=review_provider_factory,
            script_executor=script_executor,
        )

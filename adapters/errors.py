"""Typed errors for fail-closed adapter and config behavior."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadError:
    """Returned when a VCS read command fails; caller must halt."""

    command: str
    message: str = ""
    exit_code: int | None = None

    def __str__(self) -> str:
        parts = [f"ReadError({self.command!r})"]
        if self.message:
            parts.append(self.message)
        if self.exit_code is not None:
            parts.append(f"exit={self.exit_code}")
        return ": ".join(parts)


@dataclass(frozen=True)
class ConfigError(Exception):
    """Raised when config is missing, unparseable, or unsupported."""

    message: str
    path: str | None = None
    exit_code: int | None = None

    def __str__(self) -> str:
        if self.path:
            return f"{self.path}: {self.message}"
        return self.message


@dataclass(frozen=True)
class WriteError:
    """Returned when a VCS write is refused or fails."""

    command: str
    message: str
    exit_code: int | None = None

    def __str__(self) -> str:
        return f"WriteError({self.command!r}): {self.message}"

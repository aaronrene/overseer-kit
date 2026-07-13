"""Typed results for the VCS adapter interface (§4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

RegimeName = Literal["muse+git-mirror", "muse-only", "git-only"]
ShaKind = Literal["git", "muse"]


@dataclass(frozen=True)
class StatusResult:
    regime: str
    dirty: bool
    branch: str
    notes: list[str] = field(default_factory=list)
    muse_dirty: bool | None = None
    git_dirty: bool | None = None


@dataclass(frozen=True)
class HeadResult:
    sha: str
    kind: ShaKind


@dataclass(frozen=True)
class AnchorResult:
    anchor_sha: str
    source: str


@dataclass(frozen=True)
class RealignResult:
    would_import: int
    applied: bool
    from_ref: str | None
    to_ref: str | None
    reason: str | None = None


@dataclass(frozen=True)
class CommitResult:
    committed: bool
    sha: str


@dataclass(frozen=True)
class MirrorResult:
    diff_summary: str
    pushed: bool
    reason: str | None = None

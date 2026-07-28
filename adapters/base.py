"""Shared adapter helpers and base protocol."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Protocol, Union

from adapters.config import OverseerConfig
from adapters.errors import ReadError, WriteError
from adapters.runner import CommandResult, CommandRunner, SubprocessRunner, quote_arg
from adapters.types import (
    AnchorResult,
    CommitResult,
    HeadResult,
    MirrorResult,
    RealignResult,
    StatusResult,
)

AdapterResult = Union[
    StatusResult,
    HeadResult,
    AnchorResult,
    RealignResult,
    CommitResult,
    MirrorResult,
    ReadError,
    WriteError,
]


class VcsAdapter(Protocol):
    """Frozen §4 adapter interface."""

    def status(self) -> StatusResult | ReadError: ...

    def read_head(self, ref: str) -> HeadResult | ReadError: ...

    def read_canonical_anchor(self) -> AnchorResult | ReadError: ...

    def realign(self, *, dry_run: bool, max_commits: int) -> RealignResult | ReadError: ...

    def commit_feature(
        self,
        *,
        branch: str,
        message: str,
        paths: list[str],
    ) -> CommitResult | ReadError | WriteError: ...

    def mirror(self, *, dry_run: bool) -> MirrorResult | ReadError: ...


class BaseAdapter:
    """Common helpers for all backends."""

    def __init__(
        self,
        config: OverseerConfig,
        repo_root: Path,
        runner: CommandRunner | None = None,
    ) -> None:
        self.config = config
        self.repo_root = repo_root.resolve()
        self.runner = runner or SubprocessRunner()
        self._muse_cwd = self._resolve_muse_cwd()

    def _resolve_muse_cwd(self) -> Path:
        """Install root, or ``install_root / vcs.muse.working_dir`` (§K6.5.1)."""
        from cli.docs_paths import validate_muse_working_dir

        working = validate_muse_working_dir(self.repo_root, self.config.vcs.muse.working_dir)
        return working if working is not None else self.repo_root

    @property
    def regime(self) -> str:
        return self.config.vcs.regime

    @property
    def muse_cwd(self) -> Path:
        """Absolute directory passed to ``muse -C``."""
        return self._muse_cwd

    def _git(self, *args: str) -> CommandResult | ReadError:
        cmd = "git " + " ".join(quote_arg(a) for a in args)
        result = self.runner.run(cmd, cwd=str(self.repo_root))
        if not result.ok:
            return ReadError(cmd, result.stderr or result.stdout, result.exit_code)
        return result

    def _muse(self, *args: str) -> CommandResult | ReadError:
        cmd = (
            "muse -C "
            + quote_arg(str(self._muse_cwd))
            + " "
            + " ".join(quote_arg(a) for a in args)
        )
        result = self.runner.run(cmd, cwd=str(self.repo_root))
        if not result.ok:
            return ReadError(cmd, result.stderr or result.stdout, result.exit_code)
        return result

    def _muse_rev_parse_sha(self, ref: str) -> "HeadResult | ReadError":
        """Resolve a muse ref to its commit id via ``muse rev-parse`` (Muse 0.2+).

        Muse 0.2.x prints the commit id as a bare string on stdout (exit 0).
        On failure (unknown ref / empty repo) it exits non-zero with JSON on
        stdout — ``_muse`` already converts non-zero exits to ``ReadError``,
        so by the time we read ``result.stdout`` the value is always a plain SHA.
        """
        result = self._muse("rev-parse", ref)
        if isinstance(result, ReadError):
            return result
        sha = result.stdout.strip()
        if not sha:
            return ReadError(f"muse rev-parse {ref}", "empty sha")
        return HeadResult(sha=sha, kind="muse")

    def _muse_dirty(self) -> bool | ReadError:
        """Return Muse working-tree dirty flag (Muse 0.2+ ``status --json``; legacy ``--porcelain``)."""
        json_result = self._muse("status", "--json")
        if not isinstance(json_result, ReadError):
            try:
                payload = json.loads(json_result.stdout)
            except json.JSONDecodeError:
                return ReadError(
                    "muse status --json",
                    "invalid JSON from muse status",
                )
            if isinstance(payload, dict):
                if "dirty" in payload:
                    return bool(payload["dirty"])
                total = payload.get("total_changes")
                if isinstance(total, int):
                    return total > 0
            return ReadError("muse status --json", "missing dirty/total_changes field")

        porcelain = self._muse("status", "--porcelain")
        if isinstance(porcelain, ReadError):
            return porcelain
        return bool(porcelain.stdout.strip())

    def _is_protected_branch(self, branch: str) -> bool:
        git_main = self.config.vcs.git.main_branch
        muse_main = self.config.vcs.muse.main_branch
        normalized = branch.removeprefix("muse:").removeprefix("refs/heads/")
        protected = {git_main}
        if muse_main:
            protected.add(muse_main)
        return normalized in protected

    def _validate_paths(self, paths: list[str]) -> ReadError | None:
        for path in paths:
            if not path or path.startswith("-") or ".." in Path(path).parts:
                return ReadError(
                    "commit_feature",
                    f"refused unsafe path: {path!r}",
                )
        return None


BRIDGE_SHA_RE = re.compile(
    r'^\s*git_sha\s*=\s*"([0-9a-fA-F]+)"\s*$',
    re.MULTILINE,
)

BRIDGE_MUSE_COMMIT_RE = re.compile(
    r'^\s*muse_commit_id\s*=\s*"([^"]+)"\s*$',
    re.MULTILINE,
)


def _bridge_section_body(repo_root: Path, section: str) -> str | None:
    """Return the body of ``[section]`` from ``.muse/git-bridge.toml``, or ``None``."""
    bridge_path = repo_root / ".muse" / "git-bridge.toml"
    if not bridge_path.is_file():
        return None
    text = bridge_path.read_text(encoding="utf-8")
    marker = f"[{section}]"
    if marker not in text:
        return None
    section_text = text.split(marker, 1)[1]
    if "\n[" in section_text:
        section_text = section_text.split("\n[", 1)[0]
    return section_text


def bridge_section_present(repo_root: Path, section: str) -> bool:
    """True when ``.muse/git-bridge.toml`` contains a ``[section]`` header."""
    return _bridge_section_body(repo_root, section) is not None


def read_bridge_git_sha(repo_root: Path, section: str) -> str | None:
    """Read ``git_sha`` from ``.muse/git-bridge.toml`` for ``last_export`` or ``last_import``."""
    section_text = _bridge_section_body(repo_root, section)
    if section_text is None:
        return None
    match = BRIDGE_SHA_RE.search(section_text)
    return match.group(1) if match else None


def read_bridge_muse_commit_id(repo_root: Path, section: str) -> str | None:
    """Read ``muse_commit_id`` from ``.muse/git-bridge.toml`` (Muse ID space).

    Used for D2 / canonical-anchor equality under Muse 0.2.x content-hash tips.
    ``git_sha`` remains for realign ``from_ref`` / Git ancestry only.
    """
    section_text = _bridge_section_body(repo_root, section)
    if section_text is None:
        return None
    match = BRIDGE_MUSE_COMMIT_RE.search(section_text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None

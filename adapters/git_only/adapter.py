"""Git-only VCS adapter backend (§4)."""

from __future__ import annotations

from adapters.base import BaseAdapter
from adapters.errors import ReadError, WriteError
from adapters.runner import CommandResult
from adapters.types import (
    AnchorResult,
    CommitResult,
    HeadResult,
    MirrorResult,
    RealignResult,
    StatusResult,
)


class GitOnlyAdapter(BaseAdapter):
    """Single-history Git backend for external developers."""

    def status(self) -> StatusResult | ReadError:
        branch_result = self._git("rev-parse", "--abbrev-ref", "HEAD")
        if isinstance(branch_result, ReadError):
            return branch_result
        dirty_result = self._git("status", "--porcelain")
        if isinstance(dirty_result, ReadError):
            return dirty_result
        git_is_dirty = bool(dirty_result.stdout.strip())
        return StatusResult(
            regime=self.regime,
            dirty=git_is_dirty,
            branch=branch_result.stdout,
            notes=["canonical=git", "single-history"],
            muse_dirty=None,
            git_dirty=git_is_dirty,
        )

    def read_head(self, ref: str) -> HeadResult | ReadError:
        if ref.startswith("muse:"):
            return ReadError(
                "read_head",
                "muse refs forbidden in git-only regime",
            )
        result = self._git("rev-parse", ref)
        if isinstance(result, ReadError):
            return result
        sha = result.stdout.splitlines()[-1].strip()
        if not sha:
            return ReadError(f"git rev-parse {ref}", "empty sha")
        return HeadResult(sha=sha, kind="git")

    def read_canonical_anchor(self) -> AnchorResult | ReadError:
        remote = self.config.vcs.git.remote
        main = self.config.vcs.git.main_branch
        ref = f"{remote}/{main}"
        head = self.read_head(ref)
        if isinstance(head, ReadError):
            return head
        return AnchorResult(anchor_sha=head.sha, source=ref)

    def realign(self, *, dry_run: bool, max_commits: int) -> RealignResult:
        return RealignResult(
            would_import=0,
            applied=False,
            from_ref=None,
            to_ref=None,
            reason="single-history",
        )

    def commit_feature(
        self,
        *,
        branch: str,
        message: str,
        paths: list[str],
    ) -> CommitResult | ReadError | WriteError:
        unsafe = self._validate_paths(paths)
        if unsafe:
            return unsafe
        if self._is_protected_branch(branch):
            return WriteError(
                "commit_feature",
                f"refused protected branch {branch!r}",
            )

        # §GSW.6.1: skip checkout when HEAD is already on the branch — the
        # engine switches before writing docs, so a dirty tree here is normal.
        current = self._git("rev-parse", "--abbrev-ref", "HEAD")
        if isinstance(current, ReadError):
            return current
        if current.stdout.strip() != branch:
            checkout = self._git("checkout", branch)
            if isinstance(checkout, ReadError):
                return checkout

        if paths:
            add = self._git("add", "--", *paths)
            if isinstance(add, ReadError):
                return add

        commit = self._git("commit", "-m", message)
        if isinstance(commit, ReadError):
            return commit

        head = self._git("rev-parse", "HEAD")
        if isinstance(head, ReadError):
            return head
        return CommitResult(committed=True, sha=head.stdout.strip())

    def mirror(self, *, dry_run: bool) -> MirrorResult:
        return MirrorResult(
            diff_summary="",
            pushed=False,
            reason="single-history",
        )

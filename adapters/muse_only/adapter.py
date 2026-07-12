"""Muse-only VCS adapter backend (§4)."""

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

GIT_FORBIDDEN = "git forbidden in this regime"


class MuseOnlyAdapter(BaseAdapter):
    """MuseHub backend — git and mirror are hard no-ops."""

    def status(self) -> StatusResult | ReadError:
        branch_result = self._muse("branch", "--show-current")
        if isinstance(branch_result, ReadError):
            return branch_result
        dirty_result = self._muse_dirty()
        if isinstance(dirty_result, ReadError):
            return dirty_result
        return StatusResult(
            regime=self.regime,
            dirty=dirty_result,
            branch=branch_result.stdout,
            notes=["canonical=muse", "git-forbidden"],
        )

    def read_head(self, ref: str) -> HeadResult | ReadError:
        if ref.startswith("origin/") or ref.startswith(self.config.vcs.git.remote + "/"):
            return ReadError("read_head", GIT_FORBIDDEN)
        muse_ref = ref.removeprefix("muse:")
        result = self._muse("log", "-1", "--format=%H", muse_ref)
        if isinstance(result, ReadError):
            return result
        sha = result.stdout.strip()
        if not sha:
            return ReadError(f"muse log {muse_ref}", "empty sha")
        return HeadResult(sha=sha, kind="muse")

    def read_canonical_anchor(self) -> AnchorResult | ReadError:
        main = self.config.vcs.muse.main_branch
        if not main:
            return ReadError("read_canonical_anchor", "muse.main_branch not configured")
        head = self.read_head(f"muse:{main}")
        if isinstance(head, ReadError):
            return head
        return AnchorResult(anchor_sha=head.sha, source=f"muse:{main}")

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

        checkout = self._muse("checkout", branch)
        if isinstance(checkout, ReadError):
            return checkout

        if paths:
            for path in paths:
                add = self._muse("add", path)
                if isinstance(add, ReadError):
                    return add

        commit = self._muse("commit", "-m", message)
        if isinstance(commit, ReadError):
            return commit

        head = self._muse("log", "-1", "--format=%H")
        if isinstance(head, ReadError):
            return head
        return CommitResult(committed=True, sha=head.stdout.strip())

    def mirror(self, *, dry_run: bool) -> MirrorResult:
        return MirrorResult(
            diff_summary="",
            pushed=False,
            reason=GIT_FORBIDDEN,
        )

    def _git(self, *args: str) -> CommandResult | ReadError:
        return ReadError("git", GIT_FORBIDDEN)

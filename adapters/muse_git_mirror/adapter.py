"""Muse+git-mirror VCS adapter backend (§4, SD-14)."""

from __future__ import annotations

from adapters.base import (
    BaseAdapter,
    bridge_section_present,
    read_bridge_git_sha,
    read_bridge_muse_commit_id,
)
from adapters.errors import ReadError, WriteError
from adapters.types import (
    AnchorResult,
    CommitResult,
    HeadResult,
    MirrorResult,
    RealignResult,
    StatusResult,
)


class MuseGitMirrorAdapter(BaseAdapter):
    """Scooling/Knowtation backend — Muse canonical with GitHub mirror."""

    def status(self) -> StatusResult | ReadError:
        muse_branch = self._muse("rev-parse", "--abbrev-ref", "HEAD")
        if isinstance(muse_branch, ReadError):
            return muse_branch
        muse_dirty = self._muse_dirty()
        if isinstance(muse_dirty, ReadError):
            return muse_dirty
        git_branch = self._git("rev-parse", "--abbrev-ref", "HEAD")
        if isinstance(git_branch, ReadError):
            return git_branch
        git_dirty = self._git("status", "--porcelain")
        if isinstance(git_dirty, ReadError):
            return git_dirty

        notes = [
            "canonical=muse",
            f"git-branch={git_branch.stdout}",
            "sd-14: never git push origin main",
        ]
        git_is_dirty = bool(git_dirty.stdout.strip())
        dirty = muse_dirty or git_is_dirty
        return StatusResult(
            regime=self.regime,
            dirty=dirty,
            branch=muse_branch.stdout,
            notes=notes,
            muse_dirty=muse_dirty,
            git_dirty=git_is_dirty,
        )

    def read_head(self, ref: str) -> HeadResult | ReadError:
        if ref.startswith("muse:") or ref.startswith("sha256:"):
            muse_ref = ref.removeprefix("muse:")
            return self._muse_rev_parse_sha(muse_ref)

        result = self._git("rev-parse", ref)
        if isinstance(result, ReadError):
            return result
        sha = result.stdout.strip()
        if not sha:
            return ReadError(f"git rev-parse {ref}", "empty sha")
        return HeadResult(sha=sha, kind="git")

    def read_canonical_anchor(self) -> AnchorResult | ReadError:
        """Return the Muse-space bridge tip for D2 (§D2F.4.2).

        When ``[last_export]`` exists, R2 is ``muse_commit_id`` (same ID space as Muse
        tips). ``git_sha`` is intentionally not returned here — realign uses
        ``read_bridge_git_sha`` for ``from_ref`` / ancestry only.
        """
        if bridge_section_present(self.repo_root, "last_export"):
            muse_id = read_bridge_muse_commit_id(self.repo_root, "last_export")
            if muse_id:
                return AnchorResult(
                    anchor_sha=muse_id,
                    source=".muse/git-bridge.toml:last_export.muse_commit_id",
                )
            return ReadError(
                "read_canonical_anchor",
                "missing last_export.muse_commit_id",
            )

        mirror = self.config.vcs.git.mirror_branch
        remote = self.config.vcs.git.remote
        if mirror:
            ref = f"{remote}/{mirror}"
            head = self.read_head(ref)
            if not isinstance(head, ReadError):
                return AnchorResult(anchor_sha=head.sha, source=ref)

        return ReadError(
            "read_canonical_anchor",
            "no bridge anchor in .muse/git-bridge.toml or mirror ref",
        )

    def realign(self, *, dry_run: bool, max_commits: int) -> RealignResult | ReadError:
        from_ref = read_bridge_git_sha(self.repo_root, "last_import")
        if not from_ref:
            from_ref = read_bridge_git_sha(self.repo_root, "last_export")
        if not from_ref:
            return ReadError(
                "realign",
                "cannot determine from_ref (missing .muse/git-bridge.toml anchor)",
            )

        remote = self.config.vcs.git.remote
        main = self.config.vcs.git.main_branch
        to_ref = f"{remote}/{main}"
        to_head = self.read_head(to_ref)
        if isinstance(to_head, ReadError):
            return to_head

        count_cmd = self._git(
            "rev-list",
            "--count",
            f"{from_ref}..{to_head.sha}",
        )
        if isinstance(count_cmd, ReadError):
            return count_cmd
        try:
            would_import = int(count_cmd.stdout.strip())
        except ValueError:
            return ReadError(count_cmd.stdout, "invalid rev-list count")

        if would_import > max_commits:
            return RealignResult(
                would_import=would_import,
                applied=False,
                from_ref=from_ref,
                to_ref=to_head.sha,
                reason=f"exceeds max_commits ({max_commits})",
            )

        if dry_run:
            return RealignResult(
                would_import=would_import,
                applied=False,
                from_ref=from_ref,
                to_ref=to_head.sha,
                reason="dry-run",
            )

        muse_main = self.config.vcs.muse.main_branch or "main"
        import_cmd = self._muse(
            "bridge",
            "git-import",
            ".",
            "--branch",
            muse_main,
            "--from-ref",
            from_ref,
            "--incremental",
            "--preserve-merge-commits",
        )
        if isinstance(import_cmd, ReadError):
            return import_cmd

        return RealignResult(
            would_import=would_import,
            applied=True,
            from_ref=from_ref,
            to_ref=to_head.sha,
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

        # §GSW.6.1: skip checkout when Muse HEAD is already on the branch —
        # the engine's dual-HEAD ensure (§GSW.5.1) ran before doc writes, so
        # a dirty tree here must not fail the commit.
        current = self._muse("rev-parse", "--abbrev-ref", "HEAD")
        if isinstance(current, ReadError):
            return current
        if current.stdout.strip() != branch:
            # §GSW.6.2: bare checkout refuses dirty tracked files (Muse 0.2.x);
            # retry with --autoshelf to carry them. --force is forbidden.
            checkout = self._muse("checkout", branch)
            if isinstance(checkout, ReadError):
                checkout = self._muse("checkout", "--autoshelf", branch)
                if isinstance(checkout, ReadError):
                    return checkout

            current = self._muse("rev-parse", "--abbrev-ref", "HEAD")
            if isinstance(current, ReadError):
                return current
            if current.stdout.strip() != branch:
                return WriteError(
                    "commit_feature",
                    f"branch mismatch after checkout: {current.stdout!r}",
                )

        if paths:
            for path in paths:
                # Muse 0.2.x has no top-level `add`; staging is `muse code add`
                # (matches the KH2 remediation string). Found live in GSW land-b.
                add = self._muse("code", "add", path)
                if isinstance(add, ReadError):
                    return add

        commit = self._muse("commit", "-m", message)
        if isinstance(commit, ReadError):
            return commit

        head = self._muse_rev_parse_sha("HEAD")
        if isinstance(head, ReadError):
            return head
        return CommitResult(committed=True, sha=head.sha)

    def mirror(self, *, dry_run: bool) -> MirrorResult | ReadError:
        status = self._muse("bridge", "git-status")
        if isinstance(status, ReadError):
            return status
        diff_summary = status.stdout or status.stderr
        if dry_run:
            return MirrorResult(
                diff_summary=diff_summary,
                pushed=False,
                reason="dry-run",
            )
        return MirrorResult(
            diff_summary=diff_summary,
            pushed=False,
            reason="operator-authorization-required",
        )

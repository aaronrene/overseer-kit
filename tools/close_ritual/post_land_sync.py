"""Post-land main sync — optional ff-only local sync after ``ok pr-land`` (§PLS.4–§PLS.5).

Runs only after a **successful** authorized merge outcome (``merged: true``,
pre-sync exit ``0``) when ``close_ritual.post_land_sync.enabled`` is ``true``.

Frozen sequence (docs/archive/phases/PHASE-PLS-POST-LAND-MAIN-SYNC.md §PLS.4.2):

    S1  git fetch <remote>
    S2  git status --porcelain        (full tree)
    S3  dirty + require_clean_worktree → skip with warn (never clobber)
    S4  clean + HEAD != main_branch   → git checkout <main_branch>
    S5  git pull --ff-only <remote> <main_branch>
    S6  emit editor-buffer note

Never: ``--force``, ``reset --hard``, ``clean -fd``, stash-pop defaults,
non-ff merges, ``gh pr merge``, pushes, or Muse bridge export.
``muse-only`` regimes short-circuit with ``regime_skipped`` and zero git argv.
"""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

STATUS_DISABLED = "disabled"
STATUS_REGIME_SKIPPED = "regime_skipped"
STATUS_SKIPPED_DIRTY = "skipped_dirty"
STATUS_SYNCED = "synced"
STATUS_FAILED = "failed"
STATUS_NOT_APPLICABLE = "not_applicable"

#: Normative operator note after a successful ff-only sync (§PLS.4.4).
EDITOR_BUFFER_NOTE = (
    "post_land_sync: editor buffers may be stale — reload governance docs from disk; "
    "never overwrite disk with old tab content"
)

_DIRTY_SUMMARY_LIMIT = 10

GitRunner = Callable[[list[str]], "subprocess.CompletedProcess[str]"]


@dataclass
class PostLandSyncReport:
    """Always-present ``post_land_sync`` object on ``PrLandResult`` (§PLS.6.3)."""

    status: str
    remote: str = ""
    main_branch: str = ""
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def disabled_report() -> PostLandSyncReport:
    """Report for sync disabled/omitted (also for ``run_pr_land`` without config)."""
    return PostLandSyncReport(status=STATUS_DISABLED)


def not_applicable_report() -> PostLandSyncReport:
    """Report when sync is enabled but not triggered (no successful merge / dry_run)."""
    return PostLandSyncReport(status=STATUS_NOT_APPLICABLE)


def _make_default_runner(repo_root: Path) -> GitRunner:
    def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )

    return _run


def _unsafe_ref_component(value: str) -> bool:
    """Fail closed on option-injection / control chars in remote or branch names."""
    if not value or value.startswith("-"):
        return True
    return any(ch.isspace() or ord(ch) < 32 for ch in value)


def _summarize_dirty(porcelain: str) -> list[str]:
    paths = [line[3:].strip() for line in porcelain.splitlines() if line.strip()]
    shown = paths[:_DIRTY_SUMMARY_LIMIT]
    extra = len(paths) - len(shown)
    lines = [f"  dirty: {p}" for p in shown]
    if extra > 0:
        lines.append(f"  … and {extra} more dirty path(s)")
    return lines


def run_post_land_sync(
    *,
    repo_root: Path | None,
    regime: str,
    remote: str,
    main_branch: str,
    require_clean_worktree: bool = True,
    git_runner: GitRunner | None = None,
    emit: Callable[[str], None] | None = None,
) -> PostLandSyncReport:
    """Execute the frozen §PLS.4.2 sequence; never clobber a dirty tree.

    Returns a report with ``status`` in ``regime_skipped | skipped_dirty |
    synced | failed``. Callers map ``failed`` to exit ``36`` (§PLS.6.2).
    """
    messages: list[str] = []

    def _emit(line: str) -> None:
        messages.append(line)
        if emit:
            emit(line)

    if regime == "muse-only":
        _emit("post_land_sync: muse-only regime — git post-land sync does not apply")
        return PostLandSyncReport(status=STATUS_REGIME_SKIPPED, messages=messages)

    if repo_root is None:
        _emit("post_land_sync: FAILED — repo_root required when sync is enabled")
        return PostLandSyncReport(
            status=STATUS_FAILED, remote=remote, main_branch=main_branch, messages=messages
        )

    if _unsafe_ref_component(remote) or _unsafe_ref_component(main_branch):
        _emit("post_land_sync: FAILED — unsafe remote/main_branch value (fail closed)")
        return PostLandSyncReport(
            status=STATUS_FAILED, remote=remote, main_branch=main_branch, messages=messages
        )

    run = git_runner or _make_default_runner(repo_root)

    # S1 — fetch
    fetched = run(["git", "fetch", remote])
    if fetched.returncode != 0:
        _emit(
            "post_land_sync: FAILED — git fetch "
            f"{remote}: {(fetched.stderr or fetched.stdout or '').strip()}"
        )
        return PostLandSyncReport(
            status=STATUS_FAILED, remote=remote, main_branch=main_branch, messages=messages
        )

    # S2 — dirty state (full tree)
    status = run(["git", "status", "--porcelain"])
    if status.returncode != 0:
        _emit(
            "post_land_sync: FAILED — git status unreadable: "
            f"{(status.stderr or status.stdout or '').strip()}"
        )
        return PostLandSyncReport(
            status=STATUS_FAILED, remote=remote, main_branch=main_branch, messages=messages
        )

    porcelain = status.stdout or ""
    if porcelain.strip() and require_clean_worktree:
        # S3 — dirty skip: never stash/reset/checkout/pull
        _emit(
            "post_land_sync: WARN — working tree dirty; skipping local main sync "
            "(never clobbers). Clean the tree, then pull manually or re-run ok pr-land."
        )
        for line in _summarize_dirty(porcelain):
            _emit(line)
        return PostLandSyncReport(
            status=STATUS_SKIPPED_DIRTY,
            remote=remote,
            main_branch=main_branch,
            messages=messages,
        )

    # S4 — clean tree not on main → checkout main (allowed only when clean)
    head = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if head.returncode != 0:
        _emit(
            "post_land_sync: FAILED — cannot read current branch: "
            f"{(head.stderr or head.stdout or '').strip()}"
        )
        return PostLandSyncReport(
            status=STATUS_FAILED, remote=remote, main_branch=main_branch, messages=messages
        )
    current_branch = (head.stdout or "").strip()
    if current_branch != main_branch:
        checkout = run(["git", "checkout", main_branch])
        if checkout.returncode != 0:
            _emit(
                f"post_land_sync: FAILED — git checkout {main_branch}: "
                f"{(checkout.stderr or checkout.stdout or '').strip()}"
            )
            return PostLandSyncReport(
                status=STATUS_FAILED, remote=remote, main_branch=main_branch, messages=messages
            )
        _emit(f"post_land_sync: checked out {main_branch} (was {current_branch or 'detached'})")

    # S5 — ff-only pull
    pulled = run(["git", "pull", "--ff-only", remote, main_branch])
    if pulled.returncode != 0:
        _emit(
            f"post_land_sync: FAILED — git pull --ff-only {remote} {main_branch}: "
            f"{(pulled.stderr or pulled.stdout or '').strip()}"
        )
        return PostLandSyncReport(
            status=STATUS_FAILED, remote=remote, main_branch=main_branch, messages=messages
        )

    # S6 — success + editor-buffer note
    _emit(f"post_land_sync: local {main_branch} fast-forwarded to {remote}/{main_branch}")
    _emit(EDITOR_BUFFER_NOTE)
    return PostLandSyncReport(
        status=STATUS_SYNCED, remote=remote, main_branch=main_branch, messages=messages
    )

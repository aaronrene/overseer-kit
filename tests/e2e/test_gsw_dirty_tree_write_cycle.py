"""E2E: dirty-tree ``governance-sync --write`` on ALL three regimes (§GSW.10 e2e).

This is the frozen coverage-gap close: the live 2026-07-31 incident shipped
because dirty-tree ``--write`` existed only for ``git-only``. Each fixture
starts on ``main`` with a dirty working tree; the apply path must
create/switch to the sync feature branch, patch docs, and commit —
leaving ``main`` untouched and never using ``--force``.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def test_git_only_dirty_tree_write(tmp_path: Path) -> None:
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(tmp_path, "git-only", git_dirty=True)

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
    assert code == 0
    assert runner.git_branch == _feature_branch()
    assert "main" in runner.git_branches  # main still exists, untouched
    assert "cafebabe" in handover_path.read_text(encoding="utf-8")
    # PR URL print rules unchanged for git regimes (operator-gated, never auto-open).
    assert "docs-only PR URL (operator-gated" in buf.getvalue()
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(_feature_branch() in c for c in push_calls)
    assert not any(c.rstrip().endswith(" main") for c in push_calls)
    assert not any("--force" in c for c, _ in runner.calls)


def test_muse_only_dirty_tree_write_never_invokes_git(tmp_path: Path) -> None:
    handover_path, _ = seed_gsw_repo(tmp_path, "muse-only")
    original_handover = handover_path.read_text(encoding="utf-8")
    # Feature branch pre-exists (same-day retry — the live incident shape):
    # bare dirty checkout is refused, so the dirty-carry guard must engage.
    runner = gsw_runner(
        tmp_path,
        "muse-only",
        muse_dirty=True,
        existing_muse_branches={_feature_branch()},
    )

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
    assert code == 0
    assert runner.muse_branch == _feature_branch()
    assert handover_path.read_text(encoding="utf-8") != original_handover
    assert any("--autoshelf" in c for c, _ in runner.calls)
    # §GSW.8 least privilege: muse-only never invokes git/gh.
    assert not any(c.startswith(("git ", "gh ")) for c, _ in runner.calls)
    assert "docs-only PR URL" not in buf.getvalue()
    assert not any("--force" in c for c, _ in runner.calls)


def test_muse_git_mirror_dirty_tree_write_closes_live_incident(tmp_path: Path) -> None:
    """The exact live failure shape: muse+git-mirror, dirty tree, feature branch
    already created by a prior failed run — the sync must now succeed."""
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, "muse+git-mirror")
    runner = gsw_runner(
        tmp_path,
        "muse+git-mirror",
        git_dirty=True,
        muse_dirty=True,
        existing_git_branches={_feature_branch()},
        existing_muse_branches={_feature_branch()},
    )

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run_cli(
            ["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root()
        )
    assert code == 0
    # Dual-HEAD success posture: both histories on the sync branch (§GSW.5.1).
    assert runner.git_branch == _feature_branch()
    assert runner.muse_branch == _feature_branch()
    assert "main" in runner.git_branches and "main" in runner.muse_branches
    assert "cafebabe" in handover_path.read_text(encoding="utf-8")
    # Muse dirty-carry engaged instead of the live defect's bare-checkout failure.
    assert any(c.startswith("muse") and "--autoshelf" in c for c, _ in runner.calls)
    # Muse commit substrate; git push of the feature branch only.
    assert any(c.startswith("muse") and " commit " in c for c, _ in runner.calls)
    push_calls = [c for c, _ in runner.calls if c.startswith("git push")]
    assert push_calls and all(_feature_branch() in c for c in push_calls)
    assert "docs-only PR URL (operator-gated" in buf.getvalue()
    assert not any("--force" in c for c, _ in runner.calls)

"""Unit tests for the §GSW governance-sync write-path order (§GSW.10 unit tier).

Covers: apply-plan ordering (realign → branch ensure → doc writes),
``commit_feature`` already-on-branch short-circuit for all three adapters,
Muse dirty-carry checkout, branch-state capture/restore, and
marker-not-written-on-commit-failure.
"""

from __future__ import annotations

from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    adapter_for,
    fail,
    gsw_runner,
    make_runner,
    ok,
    run_cli,
    seed_gsw_repo,
)
from tools.governance_hygiene.engine import (
    BranchState,
    _capture_branch_state,
    _restore_branch_state,
)


class _EventRunner:
    """Wrap a runner and interleave its commands into a shared event list."""

    def __init__(self, inner, events: list) -> None:
        self.inner = inner
        self.events = events

    def run(self, command: str, *, cwd: str | None = None):
        self.events.append(("cmd", command))
        return self.inner.run(command, cwd=cwd)

    @property
    def calls(self):
        return self.inner.calls


def test_apply_plan_realign_then_ensure_then_writes(tmp_path: Path, monkeypatch) -> None:
    """§GSW.3.1: realign runs on the original branch before branch ensure,
    and no doc write precedes successful branch ensure."""
    seed_gsw_repo(tmp_path, "git-only")
    events: list = []

    from tools.governance_hygiene import engine as engine_mod

    real_guard = engine_mod.execute_realign_guard

    def recording_guard(config, adapter, reads, drift, *, dry_run):
        events.append(("realign", dry_run))
        return real_guard(config, adapter, reads, drift, dry_run=dry_run)

    real_write = engine_mod.atomic_write_text

    def recording_write(path: Path, text: str) -> None:
        events.append(("write", path.name))
        real_write(path, text)

    monkeypatch.setattr(engine_mod, "execute_realign_guard", recording_guard)
    monkeypatch.setattr(engine_mod, "atomic_write_text", recording_write)

    runner = _EventRunner(gsw_runner(tmp_path, "git-only"), events)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0

    realign_apply = events.index(("realign", False))
    first_checkout = next(
        index for index, event in enumerate(events)
        if event[0] == "cmd" and "git checkout -b" in event[1]
    )
    doc_writes = [
        index for index, event in enumerate(events)
        if event[0] == "write" and event[1] in {"OVERSEER-HANDOVER.md", "ROADMAP.md"}
    ]
    assert doc_writes, "expected handover/roadmap writes"
    assert realign_apply < first_checkout, "realign must run before branch ensure"
    assert first_checkout < min(doc_writes), "no doc write may precede branch ensure"


def test_commit_feature_short_circuit_git_only(git_only_config, repo_root) -> None:
    """§GSW.6.1: already on branch → skip checkout, commit dirty docs."""
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("feat/gsw"),
            "git add": ok(""),
            "git commit": ok(""),
            "git rev-parse HEAD": ok("feedface"),
        }
    )
    adapter = adapter_for(git_only_config, repo_root, runner)
    result = adapter.commit_feature(branch="feat/gsw", message="m", paths=["docs/ROADMAP.md"])
    assert result.committed is True
    assert not any("checkout" in call[0] for call in runner.calls)


def test_commit_feature_short_circuit_muse_only(muse_only_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("feat/gsw"),
            f"muse -C {root} code add": ok(""),
            f"muse -C {root} commit": ok(""),
            f"muse -C {root} rev-parse HEAD": ok("sha256:abc"),
        }
    )
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.commit_feature(branch="feat/gsw", message="m", paths=["docs/R.md"])
    assert result.committed is True
    assert not any("checkout" in call[0] for call in runner.calls)
    _assert_muse_stage_uses_code_add(runner.calls)


def test_commit_feature_short_circuit_muse_git_mirror(muse_git_mirror_config, repo_root) -> None:
    root = str(repo_root)
    runner = make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok("feat/gsw"),
            f"muse -C {root} code add": ok(""),
            f"muse -C {root} commit": ok(""),
            f"muse -C {root} rev-parse HEAD": ok("sha256:abc"),
        }
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.commit_feature(branch="feat/gsw", message="m", paths=["docs/R.md"])
    assert result.committed is True
    assert not any("checkout" in call[0] for call in runner.calls)
    _assert_muse_stage_uses_code_add(runner.calls)


def _assert_muse_stage_uses_code_add(calls) -> None:
    """Live Muse 0.2.x has no top-level `add` — staging must be `muse code add`
    (GSW land-b live regression)."""
    stage_calls = [call[0] for call in calls if " add " in call[0] or call[0].endswith(" add")]
    assert stage_calls, "expected a staging command"
    for command in stage_calls:
        assert " code add" in command, f"bare `muse add` is not a live subcommand: {command}"


def test_muse_only_dirty_off_branch_uses_autoshelf(muse_only_config, repo_root) -> None:
    """§GSW.6.2: off-branch + dirty tree → dirty-carry flag, never bare-checkout-only."""
    runner = gsw_runner(
        repo_root,
        "muse-only",
        muse_branch="main",
        muse_dirty=True,
        existing_muse_branches={"feat/gsw"},
    )
    adapter = adapter_for(muse_only_config, repo_root, runner)
    result = adapter.commit_feature(branch="feat/gsw", message="m", paths=["docs/R.md"])
    assert result.committed is True
    assert runner.muse_branch == "feat/gsw"
    assert any("--autoshelf" in call[0] for call in runner.calls)
    assert not any("--force" in call[0] for call in runner.calls)


def test_muse_git_mirror_dirty_off_branch_uses_autoshelf(muse_git_mirror_config, repo_root) -> None:
    runner = gsw_runner(
        repo_root,
        "muse+git-mirror",
        muse_branch="main",
        muse_dirty=True,
        existing_muse_branches={"feat/gsw"},
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    result = adapter.commit_feature(branch="feat/gsw", message="m", paths=["docs/R.md"])
    assert result.committed is True
    assert runner.muse_branch == "feat/gsw"
    assert any("--autoshelf" in call[0] for call in runner.calls)
    assert not any("--force" in call[0] for call in runner.calls)


def test_capture_branch_state_fails_closed_on_unreadable_head(
    git_only_config, repo_root
) -> None:
    """§GSW.4.1: unreadable HEAD → (None, failing command); no fabrication."""
    runner = make_runner({"git rev-parse --abbrev-ref HEAD": fail("bad head")})
    adapter = adapter_for(git_only_config, repo_root, runner)
    state, command = _capture_branch_state(git_only_config, adapter, runner, repo_root)
    assert state is None
    assert command == "git rev-parse --abbrev-ref HEAD"


def test_capture_branch_state_dual_fields_for_mirror(muse_git_mirror_config, repo_root) -> None:
    runner = gsw_runner(repo_root, "muse+git-mirror", git_branch="work", muse_branch="work")
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    state, command = _capture_branch_state(muse_git_mirror_config, adapter, runner, repo_root)
    assert command is None
    assert state == BranchState(git_branch="work", muse_branch="work")


def test_restore_branch_state_restores_each_regime(
    git_only_config, muse_only_config, muse_git_mirror_config, repo_root
) -> None:
    """§GSW.4.2: rollback returns HEAD(s) to the captured original branch."""
    cases = [
        (git_only_config, "git-only"),
        (muse_only_config, "muse-only"),
        (muse_git_mirror_config, "muse+git-mirror"),
    ]
    for config, regime in cases:
        runner = gsw_runner(
            repo_root,
            regime,
            git_branch="feat/gsw",
            muse_branch="feat/gsw",
            existing_git_branches={"main"},
            existing_muse_branches={"main"},
        )
        adapter = adapter_for(config, repo_root, runner)
        state = BranchState(git_branch="main", muse_branch="main")
        errors = _restore_branch_state(config, adapter, runner, repo_root, state)
        assert errors == ()
        if regime in {"git-only", "muse+git-mirror"}:
            assert runner.git_branch == "main"
        if regime in {"muse-only", "muse+git-mirror"}:
            assert runner.muse_branch == "main"
        assert not any("--force" in call[0] for call in runner.calls)


def test_restore_branch_state_dirty_muse_uses_autoshelf(
    muse_git_mirror_config, repo_root
) -> None:
    """§GSW.4.3: dirty Muse restore falls back to --autoshelf, never --force."""
    runner = gsw_runner(
        repo_root,
        "muse+git-mirror",
        git_branch="feat/gsw",
        muse_branch="feat/gsw",
        muse_dirty=True,
        existing_git_branches={"main"},
        existing_muse_branches={"main"},
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, runner)
    state = BranchState(git_branch="main", muse_branch="main")
    errors = _restore_branch_state(muse_git_mirror_config, adapter, runner, repo_root, state)
    assert errors == ()
    assert runner.muse_branch == "main"
    assert runner.git_branch == "main"
    assert any("--autoshelf" in call[0] for call in runner.calls)
    assert not any("--force" in call[0] for call in runner.calls)


def test_marker_not_written_when_commit_fails(tmp_path: Path) -> None:
    """§GSW.3.4: sync marker is written only after successful commit_feature."""
    seed_gsw_repo(tmp_path, "git-only")
    runner = gsw_runner(tmp_path, "git-only", git_commit_fails=True)
    code = run_cli(["governance-sync", "--write"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 2
    assert not (tmp_path / ".overseer" / "last_governance_sync").exists()
    assert runner.git_branch == "main"

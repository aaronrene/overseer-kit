"""Integration tests for §GSW write order on all three regime fixtures.

Injected-runner ``--write`` per regime: the call/event log must show
realign (or skip) → branch ensure → doc writes → commit (§GSW.10
integration tier). Docs become dirty only after branch ensure.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import gsw_runner, run_cli, seed_gsw_repo


def _feature_branch() -> str:
    return f"feat/governance-sync-{date.today().isoformat()}"


def _events_for_write(tmp_path: Path, regime: str, monkeypatch, **runner_kwargs):
    """Run ``governance-sync --write`` recording commands + doc writes in order."""
    handover_path, roadmap_path = seed_gsw_repo(tmp_path, regime)
    events: list = []

    from tools.governance_hygiene import engine as engine_mod

    real_write = engine_mod.atomic_write_text

    def recording_write(path: Path, text: str) -> None:
        events.append(("write", path.name))
        real_write(path, text)

    monkeypatch.setattr(engine_mod, "atomic_write_text", recording_write)

    inner = gsw_runner(tmp_path, regime, **runner_kwargs)

    class Wrapper:
        def run(self, command: str, *, cwd: str | None = None):
            events.append(("cmd", command))
            return inner.run(command, cwd=cwd)

    code = run_cli(
        ["governance-sync", "--write"], cwd=tmp_path, runner=Wrapper(), kit=kit_root()
    )
    return code, events, inner, (handover_path, roadmap_path)


def _first_index(events, predicate) -> int:
    return next(index for index, event in enumerate(events) if predicate(event))


def _doc_write_indexes(events, names) -> list[int]:
    return [
        index
        for index, event in enumerate(events)
        if event[0] == "write" and event[1] in names
    ]


def test_git_only_write_order(tmp_path: Path, monkeypatch) -> None:
    code, events, runner, _ = _events_for_write(tmp_path, "git-only", monkeypatch)
    assert code == 0
    ensure = _first_index(events, lambda e: e[0] == "cmd" and "git checkout -b" in e[1])
    writes = _doc_write_indexes(events, {"OVERSEER-HANDOVER.md", "ROADMAP.md"})
    commit = _first_index(events, lambda e: e[0] == "cmd" and e[1].startswith("git commit"))
    assert ensure < min(writes) < max(writes) < commit
    assert runner.git_branch == _feature_branch()
    assert not any(e[0] == "cmd" and e[1].startswith("muse") for e in events)


def test_muse_only_write_order(tmp_path: Path, monkeypatch) -> None:
    code, events, runner, docs = _events_for_write(tmp_path, "muse-only", monkeypatch)
    assert code == 0
    ensure = _first_index(
        events, lambda e: e[0] == "cmd" and "checkout -b" in e[1] and e[1].startswith("muse")
    )
    writes = _doc_write_indexes(
        events, {"MUSEHUB-OVERSEER-HANDOVER.md", "MUSEHUB-ROADMAP.md"}
    )
    commit = _first_index(
        events, lambda e: e[0] == "cmd" and e[1].startswith("muse") and " commit " in e[1]
    )
    assert ensure < min(writes) < max(writes) < commit
    assert runner.muse_branch == _feature_branch()
    assert not any(e[0] == "cmd" and e[1].startswith(("git ", "gh ")) for e in events)


def test_muse_git_mirror_dual_head_before_writes(tmp_path: Path, monkeypatch) -> None:
    """§GSW.5.1: both Muse HEAD and Git HEAD are on the feature branch before doc writes."""
    code, events, runner, _ = _events_for_write(tmp_path, "muse+git-mirror", monkeypatch)
    assert code == 0
    muse_ensure = _first_index(
        events, lambda e: e[0] == "cmd" and e[1].startswith("muse") and "checkout -b" in e[1]
    )
    git_ensure = _first_index(
        events, lambda e: e[0] == "cmd" and "git checkout -b" in e[1]
    )
    writes = _doc_write_indexes(events, {"OVERSEER-HANDOVER.md", "ROADMAP.md"})
    commit = _first_index(
        events, lambda e: e[0] == "cmd" and e[1].startswith("muse") and " commit " in e[1]
    )
    assert muse_ensure < min(writes)
    assert git_ensure < min(writes)
    assert max(writes) < commit
    assert runner.git_branch == _feature_branch()
    assert runner.muse_branch == _feature_branch()


def test_muse_git_mirror_realign_runs_before_branch_ensure(tmp_path: Path, monkeypatch) -> None:
    """§GSW.3.1 step B: realign apply (git-import) stays on the original branch —
    strictly before the feature-branch ensure and all doc writes."""
    # D2 drift: R3 reads a moved muse tip; post-apply verification re-reads the
    # bridge-matching tip (sequenced rev-parse values).
    code, events, runner, _ = _events_for_write(
        tmp_path,
        "muse+git-mirror",
        monkeypatch,
        muse_rev_parse_main_values=["sha256:moved", "sha256:musetip"],
    )
    assert code == 0
    realign = _first_index(events, lambda e: e[0] == "cmd" and "git-import" in e[1])
    ensure = _first_index(events, lambda e: e[0] == "cmd" and "checkout -b" in e[1])
    writes = _doc_write_indexes(events, {"OVERSEER-HANDOVER.md", "ROADMAP.md"})
    assert realign < ensure < min(writes)

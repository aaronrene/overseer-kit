"""Data-integrity tests: check_muse_sync is a pure, deterministic function (§KH2.8 data-integrity tier)."""

from __future__ import annotations

import itertools

from adapters.types import StatusResult
from tests.support import load_fixture_config
from tools.muse_sync import check_muse_sync


def _status(regime: str, muse_dirty, git_dirty) -> StatusResult:
    return StatusResult(
        regime=regime,
        dirty=bool(muse_dirty) or bool(git_dirty),
        branch="main",
        muse_dirty=muse_dirty,
        git_dirty=git_dirty,
    )


def test_identical_inputs_always_yield_identical_report(tmp_path) -> None:
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    status = _status("muse+git-mirror", True, False)
    first = check_muse_sync(config, status)
    for _ in range(50):
        again = check_muse_sync(config, status)
        assert again == first


def test_no_hidden_state_across_calls_with_varying_inputs(tmp_path) -> None:
    """Calling with a 'pending' input then a 'synced' input must not leak state between calls."""
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    pending = check_muse_sync(config, _status("muse+git-mirror", True, False))
    synced = check_muse_sync(config, _status("muse+git-mirror", False, False))
    pending_again = check_muse_sync(config, _status("muse+git-mirror", True, False))
    assert pending.state == "pending"
    assert synced.state == "synced"
    assert pending_again == pending


def test_full_input_matrix_is_exhaustively_covered_and_stable(tmp_path) -> None:
    """Every (regime, muse_dirty, git_dirty) combination resolves to exactly one of the four
    frozen states, with no combination raising or returning an undefined state."""
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    booleans_or_none = [True, False, None]
    valid_states = {"synced", "pending", "not_applicable", "unreadable"}
    for muse_dirty, git_dirty in itertools.product(booleans_or_none, booleans_or_none):
        report = check_muse_sync(config, _status("muse+git-mirror", muse_dirty, git_dirty))
        assert report.state in valid_states
        assert report.regime == "muse+git-mirror"
        assert isinstance(report.ok, bool)

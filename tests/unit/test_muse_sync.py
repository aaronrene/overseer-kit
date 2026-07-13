"""Unit tests for the Muse-sync hard gate (§KH2.4)."""

from __future__ import annotations

from dataclasses import fields

from adapters.types import StatusResult
from tests.support import FIXTURES, load_fixture_config
from tools.muse_sync import check_muse_sync


def _status(regime: str, *, muse_dirty: bool | None, git_dirty: bool | None) -> StatusResult:
    return StatusResult(
        regime=regime,
        dirty=bool(muse_dirty) or bool(git_dirty),
        branch="main",
        muse_dirty=muse_dirty,
        git_dirty=git_dirty,
    )


def test_status_result_new_fields_default_to_none() -> None:
    """Adding muse_dirty/git_dirty must not break existing positional/keyword construction."""
    result = StatusResult(regime="git-only", dirty=False, branch="main")
    assert result.muse_dirty is None
    assert result.git_dirty is None
    field_names = {f.name for f in fields(StatusResult)}
    assert {"muse_dirty", "git_dirty"}.issubset(field_names)


def test_git_only_is_not_applicable(tmp_path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_muse_sync(config, _status("git-only", muse_dirty=None, git_dirty=True))
    assert report.ok
    assert report.state == "not_applicable"
    assert report.remediation is None


def test_muse_only_is_not_applicable(tmp_path) -> None:
    config = load_fixture_config(tmp_path, "config-muse-only.yaml")
    report = check_muse_sync(config, _status("muse-only", muse_dirty=True, git_dirty=None))
    assert report.ok
    assert report.state == "not_applicable"


def test_mirror_pending_when_git_clean_and_muse_dirty(tmp_path) -> None:
    """The exact frozen trigger: Git already committed; Muse has not."""
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    report = check_muse_sync(
        config, _status("muse+git-mirror", muse_dirty=True, git_dirty=False)
    )
    assert not report.ok
    assert report.state == "pending"
    assert "muse commit" in report.remediation


def test_mirror_synced_when_both_clean(tmp_path) -> None:
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    report = check_muse_sync(
        config, _status("muse+git-mirror", muse_dirty=False, git_dirty=False)
    )
    assert report.ok
    assert report.state == "synced"
    assert report.remediation is None


def test_mirror_synced_when_both_dirty_mid_edit_non_trigger(tmp_path) -> None:
    """Frozen non-trigger: git_dirty=True must never yield 'pending', regardless of muse_dirty."""
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    report = check_muse_sync(
        config, _status("muse+git-mirror", muse_dirty=True, git_dirty=True)
    )
    assert report.ok
    assert report.state == "synced"


def test_mirror_synced_when_git_dirty_muse_clean_non_trigger(tmp_path) -> None:
    """Frozen non-trigger: normal mid-edit state (git dirty, muse already caught up)."""
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    report = check_muse_sync(
        config, _status("muse+git-mirror", muse_dirty=False, git_dirty=True)
    )
    assert report.ok
    assert report.state == "synced"


def test_mirror_unreadable_when_muse_dirty_unknown(tmp_path) -> None:
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    report = check_muse_sync(
        config, _status("muse+git-mirror", muse_dirty=None, git_dirty=False)
    )
    assert not report.ok
    assert report.state == "unreadable"


def test_mirror_unreadable_when_git_dirty_unknown(tmp_path) -> None:
    config = load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")
    report = check_muse_sync(
        config, _status("muse+git-mirror", muse_dirty=True, git_dirty=None)
    )
    assert not report.ok
    assert report.state == "unreadable"


def test_fixtures_dir_sane() -> None:
    """Guard the fixture path this module's other tests rely on."""
    assert (FIXTURES / "config-muse-git-mirror.yaml").is_file()

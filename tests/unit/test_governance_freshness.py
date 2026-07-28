"""Unit tests for governance freshness resolution (§GFG.9 unit)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from adapters.errors import ReadError
from adapters.types import AnchorResult, HeadResult, StatusResult
from tests.support import FIXTURES, load_fixture_config, write_config
from tools.governance_freshness import check_governance_freshness, parse_sync_marker
from tools.governance_freshness.check import SyncMarker


def _write_lock(repo: Path) -> None:
    (repo / ".overseer").mkdir(parents=True, exist_ok=True)
    (repo / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        "installed_at: \"2026-01-01T00:00:00Z\"\nsynced_at: \"2026-01-01T00:00:00Z\"\n"
        "footprint: []\n",
        encoding="utf-8",
    )


def _seed_docs(repo: Path, *, claim: str = "cafebabe") -> None:
    docs = repo / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        f"| GitHub `main` | `{claim}` |\n",
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("## Build queue\n\n", encoding="utf-8")


def _adapter(*, tip: str = "cafebabe", fail: str | None = None) -> MagicMock:
    adapter = MagicMock()
    if fail == "status":
        adapter.status.return_value = ReadError("git status", "boom")
        return adapter
    adapter.status.return_value = StatusResult(
        regime="git-only", dirty=False, branch="main", muse_dirty=None, git_dirty=False
    )
    if fail == "r1":
        adapter.read_head.return_value = ReadError("git rev-parse origin/main", "missing")
        return adapter
    adapter.read_head.return_value = HeadResult(sha=tip, kind="git")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha=tip, source="origin/main"
    )
    return adapter


def test_parse_enriched_and_legacy_marker() -> None:
    enriched = parse_sync_marker("2026-07-28T00:00:00Z\nr1=abc\nr3=def\n")
    assert isinstance(enriched, SyncMarker)
    assert enriched.timestamp == "2026-07-28T00:00:00Z"
    assert enriched.r1 == "abc"
    assert enriched.r3 == "def"
    assert enriched.legacy is False

    legacy = parse_sync_marker("2026-07-28T00:00:00Z\n")
    assert legacy is not None
    assert legacy.legacy is True
    assert legacy.r1 is None


def test_not_applicable_without_lock(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter())
    assert report.state == "not_applicable"
    assert report.ok


def test_ok_when_aligned_and_marker_matches(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    _seed_docs(tmp_path, claim="cafebabe")
    stamp = "2026-07-28T00:00:00Z"
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        f"{stamp}\nr1=cafebabe\nr3=cafebabe\n", encoding="utf-8"
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter())
    assert report.state == "ok"
    assert report.ok
    assert report.d1 == "aligned"
    assert report.d2 == "aligned"


def test_drifted_d1(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    _seed_docs(tmp_path, claim="deadbeef")
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter(tip="cafebabe"))
    assert report.state == "drifted"
    assert not report.ok
    assert report.d1 == "drifted"
    assert "governance-sync" in (report.remediation or "")


def test_drifted_d2(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    _seed_docs(tmp_path, claim="cafebabe")
    adapter = _adapter(tip="cafebabe")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha="aaaaaaaa", source="origin/main"
    )
    # R1 still cafebabe via read_head; D2 compares r2 anchor vs r3 (=r1 for git-only)
    # Force r3 path: for git-only r3 = r1, so change read_head for origin/main only once.
    # Instead make anchor differ from r1 by returning different tip from read_head vs anchor.
    adapter.read_head.return_value = HeadResult(sha="cafebabe", kind="git")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha="deadbeef00", source="weird"
    )
    # For git-only D2: if r3 is None use r1; else compare r2 to r3.
    # Actually git-only sets r3 = r1 in freshness reads, so D2 compares anchor to r1.
    # So anchor deadbeef00 vs r1 cafebabe → drifted.
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=adapter)
    assert report.state == "drifted"
    assert report.d2 == "drifted"


def test_stale_marker_missing(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    _seed_docs(tmp_path, claim="cafebabe")
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter())
    assert report.state == "stale_marker"
    assert report.marker_present is False


def test_stale_marker_r1_mismatch(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    _seed_docs(tmp_path, claim="cafebabe")
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        "2026-07-28T00:00:00Z\nr1=oldsha00\nr3=oldsha00\n", encoding="utf-8"
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter(tip="cafebabe"))
    assert report.state == "stale_marker"
    assert report.marker_present is True


def test_stale_marker_legacy_timestamp_only(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    _seed_docs(tmp_path, claim="cafebabe")
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        "2026-07-28T00:00:00Z\n", encoding="utf-8"
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter())
    assert report.state == "stale_marker"
    assert "legacy" in report.message.lower() or "timestamp" in report.message.lower()


def test_unreadable_on_r1_failure(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    _seed_docs(tmp_path)
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter(fail="r1"))
    assert report.state == "unreadable"
    assert not report.ok


def test_d3_only_drift_does_not_force_not_ok(tmp_path: Path) -> None:
    """D3 drifted alone must not fail GFG when D1/D2 aligned and marker current."""
    write_config(tmp_path, "config-git-only.yaml")
    _write_lock(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "| GitHub `main` | `cafebabe` |\n", encoding="utf-8"
    )
    # Roadmap claims MERGED for a phase with empty R4 — D3 may be aligned by vacuity.
    # Explicitly: GFG ignores D3; even if detect_drift would mark D3 drifted with PRs,
    # freshness with empty R4 stays ok when D1/D2 + marker good.
    (docs / "ROADMAP.md").write_text(
        "## Build queue\n\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        "| **Z** | Auto | MERGED | something |\n",
        encoding="utf-8",
    )
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        "2026-07-28T00:00:00Z\nr1=cafebabe\nr3=cafebabe\n", encoding="utf-8"
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=_adapter())
    # With empty R4, D3 is drifted (MERGED row with no matching PR) — GFG still ok
    assert report.ok
    assert report.state == "ok"

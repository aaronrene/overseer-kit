"""Unit tests for GFG-D2-FIX Muse ID-space D2 rule (§D2F.9 unit)."""

from __future__ import annotations

from pathlib import Path

from adapters.base import read_bridge_git_sha, read_bridge_muse_commit_id
from tools.governance_hygiene.drift import detect_drift
from tools.governance_hygiene.types import VerifiedReads


def _reads(
    *,
    r2: str,
    r3: str,
    regime: str = "muse+git-mirror",
    r1: str = "cafebabe00",
) -> VerifiedReads:
    return VerifiedReads(
        regime=regime,
        r1_github_main_sha=r1,
        r1_command="git rev-parse origin/main",
        r2_anchor_sha=r2.lower(),
        r2_source=".muse/git-bridge.toml:last_export.muse_commit_id",
        r3_canonical_main_sha=r3.lower(),
        r3_command="muse rev-parse main",
        r4_merged_prs=(),
        r5_branch="main",
        r5_dirty=False,
        r5_regime=regime,
    )


def test_d2_aligned_when_muse_commit_id_matches_sha256_tip() -> None:
    """git_sha≠muse tip alone is not D2 drift when muse_commit_id matches (§D2F.3)."""
    tip = "sha256:67001f71f4481906b1bad7a9f46ccf61f9113c44a6cf64473416c4c77a8b6116"
    # R2 is muse_commit_id (after adapter fix); git_sha is never fed into D2.
    drift = detect_drift(
        _reads(r2=tip, r3=tip),
        "| GitHub `main` | `cafebabe00` |",
        "## Build queue\n",
    )
    assert drift.d2_anchor_vs_canonical == "aligned"
    assert drift.d1_handover_vs_git == "aligned"


def test_d2_drifted_when_muse_commit_id_differs_from_tip() -> None:
    tip = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    other = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    drift = detect_drift(
        _reads(r2=other, r3=tip),
        "| GitHub `main` | `cafebabe00` |",
        "## Build queue\n",
    )
    assert drift.d2_anchor_vs_canonical == "drifted"
    assert "sha256:" in drift.details.get("d2", "")


def test_read_bridge_muse_commit_id_parses_live_shape(tmp_path: Path) -> None:
    muse = tmp_path / ".muse"
    muse.mkdir()
    (muse / "git-bridge.toml").write_text(
        """[last_import]
git_sha = "350c781cbb85556374d6dab9d12e3cccbee382fe"
muse_commit_id = "sha256:oldimport"

[last_export]
muse_branch = "main"
muse_commit_id = "sha256:67001f71f4481906b1bad7a9f46ccf61f9113c44a6cf64473416c4c77a8b6116"
git_remote = "origin"
git_ref = "muse-mirror"
git_sha = "1e734a922a8de5dcac248007b8dfb706c4a0f84e"
exported_at = "2026-07-28T04:39:34.834238+00:00"
""",
        encoding="utf-8",
    )
    muse_id = read_bridge_muse_commit_id(tmp_path, "last_export")
    git_sha = read_bridge_git_sha(tmp_path, "last_export")
    assert muse_id == (
        "sha256:67001f71f4481906b1bad7a9f46ccf61f9113c44a6cf64473416c4c77a8b6116"
    )
    assert git_sha == "1e734a922a8de5dcac248007b8dfb706c4a0f84e"
    assert muse_id != git_sha


def test_read_bridge_muse_commit_id_missing(tmp_path: Path) -> None:
    muse = tmp_path / ".muse"
    muse.mkdir()
    (muse / "git-bridge.toml").write_text(
        '[last_export]\ngit_sha = "' + ("a" * 40) + '"\n',
        encoding="utf-8",
    )
    assert read_bridge_muse_commit_id(tmp_path, "last_export") is None
    assert read_bridge_git_sha(tmp_path, "last_export") == "a" * 40

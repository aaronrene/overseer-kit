"""Integration: realign plan/verify under Muse content-hash tips (§D2F.9)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from adapters.types import AnchorResult, HeadResult, RealignResult
from tools.governance_hygiene.realign import execute_realign_guard, plan_realign
from tools.governance_hygiene.types import DriftReport, VerifiedReads


def _config(tmp_path: Path):
    from tests.support import load_fixture_config, write_config

    write_config(tmp_path, "config-muse-git-mirror.yaml")
    return load_fixture_config(tmp_path, "config-muse-git-mirror.yaml")


def _reads(*, r2_muse: str, r1: str = "b" * 40) -> VerifiedReads:
    return VerifiedReads(
        regime="muse+git-mirror",
        r1_github_main_sha=r1,
        r1_command="git rev-parse origin/main",
        r2_anchor_sha=r2_muse.lower(),
        r2_source=".muse/git-bridge.toml:last_export.muse_commit_id",
        r3_canonical_main_sha=r2_muse.lower(),
        r3_command="muse rev-parse main",
        r4_merged_prs=(),
        r5_branch="main",
        r5_dirty=False,
        r5_regime="muse+git-mirror",
    )


def test_plan_realign_skips_when_d2_aligned_despite_git_sha_mismatch(tmp_path: Path) -> None:
    tip = "sha256:" + ("a" * 64)
    git_sha = "1e734a922a8de5dcac248007b8dfb706c4a0f84e"
    muse = tmp_path / ".muse"
    muse.mkdir()
    (muse / "git-bridge.toml").write_text(
        f'[last_export]\nmuse_commit_id = "{tip}"\ngit_sha = "{git_sha}"\n',
        encoding="utf-8",
    )
    assert tip != git_sha

    config = _config(tmp_path)
    adapter = MagicMock()
    adapter.repo_root = tmp_path
    drift = DriftReport(
        d1_handover_vs_git="aligned",
        d2_anchor_vs_canonical="aligned",
        d3_queue_vs_merged="aligned",
    )
    should, reason = plan_realign(config, adapter, _reads(r2_muse=tip), drift)
    assert should is False
    assert "skip" in reason.lower()
    adapter.runner.run.assert_not_called()


def test_plan_realign_uses_git_sha_for_ancestry_not_muse_id(tmp_path: Path) -> None:
    tip = "sha256:" + ("c" * 64)
    git_sha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    main = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    muse = tmp_path / ".muse"
    muse.mkdir()
    (muse / "git-bridge.toml").write_text(
        f'[last_export]\nmuse_commit_id = "{tip}"\ngit_sha = "{git_sha}"\n',
        encoding="utf-8",
    )
    config = _config(tmp_path)
    adapter = MagicMock()
    adapter.repo_root = tmp_path
    runner = MagicMock()
    runner.run.return_value = MagicMock(ok=True)
    adapter.runner = runner

    drift = DriftReport(
        d1_handover_vs_git="aligned",
        d2_anchor_vs_canonical="drifted",
        d3_queue_vs_merged="aligned",
    )
    reads = _reads(r2_muse=tip, r1=main)
    # Force r3 differ so D2 drifted context is honest
    reads = VerifiedReads(
        regime=reads.regime,
        r1_github_main_sha=main,
        r1_command=reads.r1_command,
        r2_anchor_sha=tip.lower(),
        r2_source=reads.r2_source,
        r3_canonical_main_sha=("sha256:" + ("d" * 64)).lower(),
        r3_command=reads.r3_command,
        r4_merged_prs=(),
        r5_branch="main",
        r5_dirty=False,
        r5_regime="muse+git-mirror",
    )
    should, reason = plan_realign(config, adapter, reads, drift)
    assert should is True
    assert "superset" in reason
    cmd = runner.run.call_args[0][0]
    assert git_sha in cmd
    assert "sha256:" not in cmd


def test_execute_realign_verify_compares_muse_ids(tmp_path: Path) -> None:
    tip = "sha256:" + ("e" * 64)
    git_sha = "ffffffffffffffffffffffffffffffffffffffff"
    muse = tmp_path / ".muse"
    muse.mkdir()
    (muse / "git-bridge.toml").write_text(
        f'[last_export]\nmuse_commit_id = "{tip}"\ngit_sha = "{git_sha}"\n',
        encoding="utf-8",
    )
    config = _config(tmp_path)
    adapter = MagicMock()
    adapter.repo_root = tmp_path
    runner = MagicMock()
    runner.run.return_value = MagicMock(ok=True)
    adapter.runner = runner
    adapter.realign.return_value = RealignResult(
        would_import=2,
        applied=True,
        from_ref=git_sha,
        to_ref="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    )
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha=tip, source=".muse/git-bridge.toml:last_export.muse_commit_id"
    )
    adapter.read_head.return_value = HeadResult(sha=tip, kind="muse")

    drift = DriftReport(
        d1_handover_vs_git="aligned",
        d2_anchor_vs_canonical="drifted",
        d3_queue_vs_merged="aligned",
    )
    reads = VerifiedReads(
        regime="muse+git-mirror",
        r1_github_main_sha="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        r1_command="git rev-parse origin/main",
        r2_anchor_sha=("sha256:" + ("0" * 64)).lower(),
        r2_source=".muse/git-bridge.toml:last_export.muse_commit_id",
        r3_canonical_main_sha=tip.lower(),
        r3_command="muse rev-parse main",
        r4_merged_prs=(),
        r5_branch="main",
        r5_dirty=False,
        r5_regime="muse+git-mirror",
    )
    summary, err = execute_realign_guard(
        config, adapter, reads, drift, dry_run=False
    )
    assert err is None
    assert summary is not None
    assert "imported" in summary
    # Verify path must not require git_sha == tip
    assert git_sha != tip

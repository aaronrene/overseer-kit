"""Security: fail-closed on missing muse_commit_id; no optimistic aligned (§D2F.9)."""

from __future__ import annotations

from pathlib import Path

from adapters.errors import ReadError
from tests.support import adapter_for, make_runner


def test_missing_muse_commit_id_is_read_error_not_git_sha(
    muse_git_mirror_config, repo_root: Path
) -> None:
    muse = repo_root / ".muse"
    muse.mkdir(parents=True)
    (muse / "git-bridge.toml").write_text(
        '[last_export]\ngit_sha = "' + ("a" * 40) + '"\n',
        encoding="utf-8",
    )
    adapter = adapter_for(muse_git_mirror_config, repo_root, make_runner({}))
    result = adapter.read_canonical_anchor()
    assert isinstance(result, ReadError)
    assert "muse_commit_id" in str(result)
    # Must not silently treat git_sha as aligned anchor
    assert not hasattr(result, "anchor_sha") or getattr(result, "anchor_sha", None) is None

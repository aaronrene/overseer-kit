"""Data-integrity: muse_commit_id preserved including sha256: prefix (§D2F.9)."""

from __future__ import annotations

from pathlib import Path

from adapters.base import read_bridge_git_sha, read_bridge_muse_commit_id
from tests.support import adapter_for, make_runner


def test_muse_commit_id_roundtrip_preserves_prefix(
    muse_git_mirror_config, repo_root: Path
) -> None:
    tip = "sha256:67001f71f4481906b1bad7a9f46ccf61f9113c44a6cf64473416c4c77a8b6116"
    git_sha = "1e734a922a8de5dcac248007b8dfb706c4a0f84e"
    muse = repo_root / ".muse"
    muse.mkdir(parents=True)
    original = (
        f'[last_export]\n'
        f'muse_commit_id = "{tip}"\n'
        f'git_sha = "{git_sha}"\n'
    )
    path = muse / "git-bridge.toml"
    path.write_text(original, encoding="utf-8")

    assert read_bridge_muse_commit_id(repo_root, "last_export") == tip
    assert read_bridge_git_sha(repo_root, "last_export") == git_sha
    adapter = adapter_for(muse_git_mirror_config, repo_root, make_runner({}))
    anchor = adapter.read_canonical_anchor()
    assert anchor.anchor_sha == tip
    # Reading must not mutate bridge bytes
    assert path.read_text(encoding="utf-8") == original

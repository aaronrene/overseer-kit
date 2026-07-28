"""Performance: bridge parse is file-local, no network (§D2F.9 performance)."""

from __future__ import annotations

import time
from pathlib import Path

from adapters.base import read_bridge_git_sha, read_bridge_muse_commit_id


def test_bridge_parse_bounded_and_local(tmp_path: Path) -> None:
    tip = "sha256:" + ("f" * 64)
    git_sha = "e" * 40
    muse = tmp_path / ".muse"
    muse.mkdir()
    (muse / "git-bridge.toml").write_text(
        f'[last_export]\nmuse_commit_id = "{tip}"\ngit_sha = "{git_sha}"\n',
        encoding="utf-8",
    )
    start = time.perf_counter()
    for _ in range(200):
        assert read_bridge_muse_commit_id(tmp_path, "last_export") == tip
        assert read_bridge_git_sha(tmp_path, "last_export") == git_sha
    assert time.perf_counter() - start < 1.0

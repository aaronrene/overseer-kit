"""Stress: bridge TOML with large unrelated sections (§D2F.9 stress)."""

from __future__ import annotations

from pathlib import Path

from adapters.base import read_bridge_git_sha, read_bridge_muse_commit_id


def test_bridge_parsers_isolate_last_export_amid_noise(tmp_path: Path) -> None:
    tip = "sha256:" + ("a" * 64)
    git_sha = "b" * 40
    noise = "\n".join(f'noise_key_{i} = "x{i}"' for i in range(200))
    body = f"""[meta]
{noise}

[last_import]
git_sha = "{"c" * 40}"
muse_commit_id = "sha256:{"d" * 64}"
{noise}

[last_export]
muse_branch = "main"
muse_commit_id = "{tip}"
git_remote = "origin"
git_ref = "muse-mirror"
git_sha = "{git_sha}"
{noise}

[other]
{noise}
"""
    muse = tmp_path / ".muse"
    muse.mkdir()
    (muse / "git-bridge.toml").write_text(body, encoding="utf-8")
    assert read_bridge_muse_commit_id(tmp_path, "last_export") == tip
    assert read_bridge_git_sha(tmp_path, "last_export") == git_sha
    assert read_bridge_muse_commit_id(tmp_path, "last_import") == "sha256:" + ("d" * 64)

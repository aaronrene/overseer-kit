"""E2E: healthy muse+git-mirror bridge does not plan git-import (§D2F.9 e2e)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.support import (
    FIXTURES,
    muse_mirror_status_runner,
    ok,
    run_cli,
    seed_muse_substrate,
)


def test_healthy_bridge_status_ok_without_git_import(tmp_path: Path) -> None:
    tip = "sha256:" + ("6" * 64)
    git_sha = "1e734a922a8de5dcac248007b8dfb706c4a0f84e"
    github_main = "cafebabe00cafebabe00cafebabe00cafebabe00"
    assert tip != git_sha

    runner = muse_mirror_status_runner(tmp_path)
    root = str(tmp_path.resolve())
    runner.responses.update(
        {
            f"muse -C {root} rev-parse main": ok(tip),
            "git rev-parse origin/main": ok(github_main),
            "git rev-parse origin/muse-mirror": ok(git_sha),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                json.dumps([])
            ),
        }
    )
    seed_muse_substrate(tmp_path)
    (tmp_path / ".muse" / "git-bridge.toml").write_text(
        f"[last_export]\n"
        f'muse_commit_id = "{tip}"\n'
        f'git_sha = "{git_sha}"\n'
        f'[last_import]\ngit_sha = "{git_sha}"\n',
        encoding="utf-8",
    )

    assert (
        run_cli(
            [
                "init",
                "--from-config",
                str(FIXTURES / "config-muse-git-mirror.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )

    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    base = handover.read_text(encoding="utf-8") if handover.is_file() else ""
    handover.write_text(
        base.rstrip()
        + f"\n\n| Item | Value |\n| --- | --- |\n| GitHub `main` | `{github_main}` |\n",
        encoding="utf-8",
    )
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        f"2026-07-28T00:00:00Z\nr1={github_main}\nr3={tip}\n",
        encoding="utf-8",
    )
    # Preserve healthy bridge after any helper writes
    (tmp_path / ".muse" / "git-bridge.toml").write_text(
        f"[last_export]\n"
        f'muse_commit_id = "{tip}"\n'
        f'git_sha = "{git_sha}"\n'
        f'[last_import]\ngit_sha = "{git_sha}"\n',
        encoding="utf-8",
    )

    assert run_cli(["governance-sync", "--dry-run"], cwd=tmp_path, runner=runner) == 0
    assert (
        run_cli(
            ["status", "--json", "--exit-code"],
            cwd=tmp_path,
            runner=runner,
            json_mode=True,
        )
        == 0
    )
    assert [c for c in runner.calls if "merge-base" in c[0]] == []
    assert [c for c in runner.calls if "git-import" in c[0]] == []

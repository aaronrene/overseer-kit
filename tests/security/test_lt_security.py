"""Security tests for LT loop tightening (§LT.10)."""

from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

from tests.support import FIXTURES, KIT_ROOT, git_status_runner, load_fixture_config, run_cli
from tools.footprint_coverage import check_footprint_coverage
from tools.handover_compact import compact_handover_change_log


def test_coverage_missing_paths_are_repo_relative(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    from cli.footprint import resolve_footprint
    from cli.version_lock import ORIGIN_KIT, FootprintEntry, build_version_lock_from_entries

    files = resolve_footprint(config, kit=KIT_ROOT)
    lock = build_version_lock_from_entries(
        kit_version="0.1.0",
        config_version=1,
        entries=[
            FootprintEntry(
                path=files[0].destination,
                source=files[0].source,
                sha256="0" * 64,
                origin=ORIGIN_KIT,
            )
        ],
        installed_at="2026-01-01T00:00:00Z",
    )
    report = check_footprint_coverage(tmp_path, config, lock=lock, rendered=files, kit=KIT_ROOT)
    for path in report.missing:
        assert not Path(path).is_absolute()
        assert ".." not in Path(path).parts


def test_compact_archive_path_repo_relative(tmp_path: Path) -> None:
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    handover.parent.mkdir(parents=True, exist_ok=True)
    bullets = "\n\n".join(f"- **2026-01-{d:02d}** — e" for d in range(1, 21))
    handover.write_text(
        f"<!-- overseer:anchor:change-log -->\n{bullets}\n"
        "<!-- /overseer:anchor:change-log -->\n",
        encoding="utf-8",
    )
    report = compact_handover_change_log(config, tmp_path, keep=15, write=True)
    assert not Path(report.archive).is_absolute()
    assert ".." not in Path(report.archive).parts
    living = handover.read_text(encoding="utf-8")
    assert str(tmp_path) not in living


def test_session_start_hook_fail_open_without_ok(tmp_path: Path) -> None:
    script = KIT_ROOT / "cursor" / "hooks" / "session-start-next.sh"
    env = os.environ.copy()
    env.pop("OVERSEER_OK", None)
    env["PATH"] = "/usr/bin:/bin"
    completed = subprocess.run(
        ["sh", str(script)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    payload = json.loads(completed.stdout.strip())
    assert "additional_context" in payload
    assert "followup_message" in payload


def test_git_only_handover_compact_zero_muse_argv(tmp_path: Path) -> None:
    runner = git_status_runner()
    assert (
        run_cli(
            ["init", "--from-config", str(FIXTURES / "config-git-only.yaml"), "--non-interactive"],
            cwd=tmp_path,
            runner=runner,
        )
        == 0
    )
    handover = tmp_path / "docs" / "OVERSEER-HANDOVER.md"
    bullets = "\n\n".join(f"- **2026-01-{d:02d}** — e" for d in range(1, 21))
    text = handover.read_text(encoding="utf-8")
    if "<!-- overseer:anchor:change-log -->" in text:
        start = text.index("<!-- overseer:anchor:change-log -->")
        end = text.index("<!-- /overseer:anchor:change-log -->")
        handover.write_text(
            text[: start + len("<!-- overseer:anchor:change-log -->")]
            + "\n"
            + bullets
            + "\n"
            + text[end:],
            encoding="utf-8",
        )
    else:
        handover.write_text(
            text
            + "\n<!-- overseer:anchor:change-log -->\n"
            + bullets
            + "\n<!-- /overseer:anchor:change-log -->\n",
            encoding="utf-8",
        )
    run_cli(["handover-compact", "--write"], cwd=tmp_path, runner=runner)
    muse_calls = [c for c in runner.calls if c[0].startswith("muse")]
    assert muse_calls == []


def test_session_start_hook_fail_open_without_python3(tmp_path: Path) -> None:
    script = KIT_ROOT / "cursor" / "hooks" / "session-start-next.sh"
    env = os.environ.copy()
    env.pop("OVERSEER_OK", None)
    env["PATH"] = "/usr/bin:/bin"
    completed = subprocess.run(
        ["sh", str(script)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    assert "additional_context" in payload


def test_hook_scripts_are_executable_in_kit_source() -> None:
    for name in ("session-start-next.sh", "session-end-closeout.sh"):
        path = KIT_ROOT / "cursor" / "hooks" / name
        mode = path.stat().st_mode
        assert mode & stat.S_IXUSR

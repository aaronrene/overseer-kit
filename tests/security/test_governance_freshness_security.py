"""Security: no secrets in marker; muse-only skips git/gh; fail-closed (§GFG.9 security)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from adapters.errors import ReadError
from adapters.types import AnchorResult, HeadResult, StatusResult
from tests.support import FIXTURES, load_fixture_config, write_config
from tools.governance_freshness import check_governance_freshness


def test_marker_and_payload_have_no_secrets(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        "installed_at: \"2026-01-01T00:00:00Z\"\nsynced_at: \"2026-01-01T00:00:00Z\"\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        "| GitHub `main` | `cafebabe` |\n", encoding="utf-8"
    )
    (docs / "ROADMAP.md").write_text("## Build queue\n\n", encoding="utf-8")
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        "2026-07-28T00:00:00Z\nr1=cafebabe\nr3=cafebabe\n", encoding="utf-8"
    )
    adapter = MagicMock()
    adapter.status.return_value = StatusResult(
        regime="git-only", dirty=False, branch="main", muse_dirty=None, git_dirty=False
    )
    adapter.read_head.return_value = HeadResult(sha="cafebabe", kind="git")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha="cafebabe", source="origin/main"
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=adapter)
    blob = json.dumps(
        {
            "state": report.state,
            "message": report.message,
            "remediation": report.remediation,
            "marker_r1": report.marker_r1,
            "actual_r1": report.actual_r1,
        }
    )
    for banned in ("sk-", "API_KEY", "password", "BEGIN PRIVATE"):
        assert banned not in blob
    assert report.remediation is None or report.remediation.startswith("ok ")


def test_muse_only_never_calls_git_or_gh(tmp_path: Path) -> None:
    write_config(tmp_path, "config-muse-only.yaml")
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        "installed_at: \"2026-01-01T00:00:00Z\"\nsynced_at: \"2026-01-01T00:00:00Z\"\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text("handover\n", encoding="utf-8")
    (docs / "ROADMAP.md").write_text("## Build queue\n\n", encoding="utf-8")
    (tmp_path / ".overseer" / "last_governance_sync").write_text(
        "2026-07-28T00:00:00Z\nr1=\nr3=cafebabe\n", encoding="utf-8"
    )
    adapter = MagicMock()
    adapter.status.return_value = StatusResult(
        regime="muse-only", dirty=False, branch="main", muse_dirty=False, git_dirty=None
    )
    adapter.read_head.return_value = HeadResult(sha="cafebabe", kind="muse")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha="cafebabe", source="muse:main"
    )
    runner = MagicMock()
    config = load_fixture_config(tmp_path, "config-muse-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=adapter, runner=runner)
    assert report.ok
    for call in runner.run.call_args_list:
        cmd = call.args[0] if call.args else ""
        assert not cmd.startswith("git ")
        assert not cmd.startswith("gh ")


def test_unreadable_fails_closed_not_optimistic_ok(tmp_path: Path) -> None:
    write_config(tmp_path, "config-git-only.yaml")
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        "installed_at: \"2026-01-01T00:00:00Z\"\nsynced_at: \"2026-01-01T00:00:00Z\"\n"
        "footprint: []\n",
        encoding="utf-8",
    )
    adapter = MagicMock()
    adapter.status.return_value = ReadError("git status", "denied")
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_governance_freshness(config, tmp_path, adapter=adapter)
    assert report.state == "unreadable"
    assert not report.ok


def test_automation_template_cannot_merge_or_push() -> None:
    template = (
        FIXTURES.parent.parent
        / "cursor"
        / "automations"
        / "governance-sync-session-end.json"
    )
    raw = template.read_text(encoding="utf-8")
    assert "governance-sync --dry-run" in raw
    assert "push" not in raw.lower() or "no main merge/push" in raw.lower()
    assert "merge" not in raw.lower() or "no main merge" in raw.lower()
    assert '"command": "ok governance-sync --dry-run"' in raw

"""Security: land-closeout fail-closed, no secrets, no exec, muse-only no git/gh
(§PMHF.10 security)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from adapters.runner import RecordingRunner
from adapters.types import AnchorResult, HeadResult, StatusResult
from tests.support import (
    KIT_ROOT,
    land_a_fence_body,
    land_handover_text,
    load_fixture_config,
    seed_land_repo,
    write_config,
)
from tools.governance_hygiene.next_regen import LAND_B_REMEDIATION
from tools.land_closeout import check_land_closeout, land_closeout_payload

CI_TEMPLATE = KIT_ROOT / "templates" / "ci" / "governance-closeout-github-actions.yml"


def _adapter(tip: str = "cafebabe") -> MagicMock:
    adapter = MagicMock()
    adapter.status.return_value = StatusResult(
        regime="git-only", dirty=False, branch="main", muse_dirty=None, git_dirty=False
    )
    adapter.read_head.return_value = HeadResult(sha=tip, kind="git")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha=tip, source="origin/main"
    )
    return adapter


def test_report_does_not_echo_handover_secrets(tmp_path: Path) -> None:
    secret = "ghp_seCRETtoken1234567890abcdefFAKE"
    seed_land_repo(
        tmp_path,
        claim="deadbeef",
        handover_text=land_handover_text(
            "deadbeef",
            fence_body=land_a_fence_body(paste_extra=f"token: {secret}\n"),
        ),
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_land_closeout(config, tmp_path, adapter=_adapter())
    payload = land_closeout_payload(report)
    assert secret not in str(payload)


def test_remediation_strings_are_never_executed(tmp_path: Path) -> None:
    seed_land_repo(tmp_path, claim="deadbeef")
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    runner = RecordingRunner(responses={}, calls=[])
    report = check_land_closeout(
        config, tmp_path, adapter=_adapter(), runner=runner, probe_merged_pr=False
    )
    assert report.remediation == LAND_B_REMEDIATION
    # The remediation text is advisory only — no command containing it ever runs.
    assert not any(LAND_B_REMEDIATION[:20] in call[0] for call in runner.calls)


def test_no_write_commands_from_land_closeout(tmp_path: Path) -> None:
    seed_land_repo(
        tmp_path,
        handover_text=land_handover_text(
            "cafebabe",
            fence_body=land_a_fence_body(paste_extra="PR #206 open — waiting for merge.\n"),
        ),
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    runner = RecordingRunner(responses={}, calls=[])
    check_land_closeout(
        config, tmp_path, adapter=_adapter(), runner=runner, probe_merged_pr=True
    )
    forbidden = ("git push", "git commit", "git merge", "gh pr merge")
    for call in runner.calls:
        assert not any(call[0].startswith(cmd) for cmd in forbidden)


def test_muse_only_never_calls_git_or_gh(tmp_path: Path) -> None:
    write_config(tmp_path, "config-muse-only.yaml")
    (tmp_path / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        'installed_at: "2026-01-01T00:00:00Z"\nsynced_at: "2026-01-01T00:00:00Z"\n'
        "footprint: []\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        land_handover_text(
            "cafebabe",
            fence_body=land_a_fence_body(paste_extra="PR #206 open — waiting for merge.\n"),
        ),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text("## Build queue\n\n", encoding="utf-8")

    config = load_fixture_config(tmp_path, "config-muse-only.yaml")
    adapter = MagicMock()
    adapter.status.return_value = StatusResult(
        regime="muse-only", dirty=False, branch="main", muse_dirty=False, git_dirty=None
    )
    adapter.read_head.return_value = HeadResult(sha="cafebabe", kind="muse")
    adapter.read_canonical_anchor.return_value = AnchorResult(
        anchor_sha="cafebabe", source="muse:main"
    )
    runner = RecordingRunner(responses={}, calls=[])
    report = check_land_closeout(
        config,
        tmp_path,
        adapter=adapter,
        runner=runner,
        probe_merged_pr=True,  # must be ignored for muse-only (§PMHF.5.3)
    )
    assert report.optional_pr_merged is None
    assert not any(
        call[0].startswith("git") or call[0].startswith("gh") for call in runner.calls
    )


def test_fail_closed_on_corrupted_lock(tmp_path: Path) -> None:
    seed_land_repo(tmp_path)
    (tmp_path / ".overseer" / "version.lock").write_text(
        ":: not yaml ::\n\t{{{", encoding="utf-8"
    )
    config = load_fixture_config(tmp_path, "config-git-only.yaml")
    report = check_land_closeout(config, tmp_path, adapter=_adapter())
    assert report.state == "unreadable"
    assert not report.ok


def test_ci_template_uses_github_token_only_and_never_pushes() -> None:
    text = CI_TEMPLATE.read_text(encoding="utf-8")
    assert "secrets." not in text  # standard GITHUB_TOKEN only (github.token)
    assert "github.token" in text
    active = "\n".join(
        line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")
    )
    assert "git push" not in active
    assert "cursor" not in active.lower()  # no Cursor-only steps

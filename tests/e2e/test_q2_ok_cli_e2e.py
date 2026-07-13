"""E2E tests for Track Q / Q2b OK CLI entrypoint (§Q2A.10)."""

from __future__ import annotations

import json
from pathlib import Path

from tests.support import FIXTURES, run_shim, seed_git_repo


def test_ok_shim_fail_closed_remediation_then_status_and_review_dry_run(tmp_path: Path) -> None:
    seed_git_repo(tmp_path)
    review = run_shim(
        "ok",
        ["review", "--freeze", "docs/FREEZE.md", "--dry-run"],
        cwd=tmp_path,
    )
    assert review.exit_code == 2
    assert "run ok init first" in review.stderr

    artifact = tmp_path / "docs" / "FREEZE.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text((FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8"), encoding="utf-8")

    review_fail = run_shim(
        "ok",
        ["review", "--freeze", "docs/FREEZE.md", "--dry-run"],
        cwd=tmp_path,
    )
    assert review_fail.exit_code == 2
    assert "run ok init first" in review_fail.stderr

    status = run_shim("ok", ["status"], cwd=tmp_path)
    assert status.exit_code == 0
    assert "not initialized" in status.stdout

    init = run_shim(
        "ok",
        ["init", "--regime", "git-only", "--non-interactive"],
        cwd=tmp_path,
    )
    assert init.exit_code == 0

    status_json = run_shim("ok", ["status", "--json"], cwd=tmp_path)
    assert status_json.exit_code == 0
    payload = json.loads(status_json.stdout)
    assert payload["initialized"] is True

    review = run_shim(
        "ok",
        ["review", "--freeze", "docs/FREEZE.md", "--dry-run"],
        cwd=tmp_path,
    )
    assert review.exit_code in {0, 7, 8}

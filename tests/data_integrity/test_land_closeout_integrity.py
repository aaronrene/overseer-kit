"""Data integrity: land-closeout never writes; CI template never applies to main
(§PMHF.10 data-integrity)."""

from __future__ import annotations

import json
from pathlib import Path

from cli.kit_root import kit_root
from tests.support import (
    KIT_ROOT,
    git_status_runner,
    make_runner,
    ok,
    run_cli,
    seed_land_repo,
)

CI_TEMPLATE = KIT_ROOT / "templates" / "ci" / "governance-closeout-github-actions.yml"


def _doc_bytes(tmp_path: Path) -> dict[str, bytes]:
    docs = tmp_path / "docs"
    return {p.name: p.read_bytes() for p in sorted(docs.glob("*.md"))}


def test_status_and_land_closeout_never_write_docs(tmp_path: Path, capsys) -> None:
    seed_land_repo(tmp_path, claim="deadbeef")  # drifted → both surfaces report failure
    before = _doc_bytes(tmp_path)
    marker_before = (tmp_path / ".overseer" / "last_governance_sync").read_bytes()

    assert (
        run_cli(
            ["status", "--json", "--exit-code"],
            cwd=tmp_path,
            runner=git_status_runner(tip="cafebabe"),
            json_mode=True,
        )
        == 2
    )
    assert (
        run_cli(
            ["land-closeout", "--json"],
            cwd=tmp_path,
            runner=git_status_runner(tip="cafebabe"),
            json_mode=True,
        )
        == 2
    )
    capsys.readouterr()

    assert _doc_bytes(tmp_path) == before
    assert (tmp_path / ".overseer" / "last_governance_sync").read_bytes() == marker_before


def test_land_closeout_idempotent(tmp_path: Path, capsys) -> None:
    seed_land_repo(tmp_path, claim="deadbeef")
    outputs = []
    for _ in range(2):
        capsys.readouterr()
        code = run_cli(
            ["land-closeout", "--json"],
            cwd=tmp_path,
            runner=git_status_runner(tip="cafebabe"),
            json_mode=True,
        )
        assert code == 2
        outputs.append(json.loads(capsys.readouterr().out))
    assert outputs[0] == outputs[1]


def test_ci_template_has_no_apply_to_main_step() -> None:
    text = CI_TEMPLATE.read_text(encoding="utf-8")
    active_lines = [
        line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    active = "\n".join(active_lines)
    assert "git push" not in active  # frozen ban: never pushes from the workflow
    assert "--write" not in active  # governance-sync stays dry-run in CI
    assert "governance-sync --dry-run" in active
    assert "land-closeout --probe-merged-pr" in active
    assert "workflow_dispatch" in active
    assert "contents: read" in active  # read-only checkout — cannot write main


def test_dry_run_governance_sync_still_only_stamps_marker(tmp_path: Path) -> None:
    # GFG carve-out unchanged: aligned dry-run stamps the local marker only.
    seed_land_repo(tmp_path, claim="cafebabe", marker_tip=None)
    before = _doc_bytes(tmp_path)
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok(
                "[]"
            ),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    code = run_cli(["governance-sync"], cwd=tmp_path, runner=runner, kit=kit_root())
    assert code == 0
    assert _doc_bytes(tmp_path) == before  # no governance-doc writes on dry-run
    marker = tmp_path / ".overseer" / "last_governance_sync"
    assert marker.is_file()
    assert "r1=cafebabe" in marker.read_text(encoding="utf-8")

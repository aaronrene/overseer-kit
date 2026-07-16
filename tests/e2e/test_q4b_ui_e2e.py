"""End-to-end tests for Track Q / Q4b Path B UI redesign (§Q4A.15)."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from cli.kit_root import kit_root
from tests.fixtures.app import free_port, seed_app_e2e_repo, seed_app_repo, start_test_app
from tests.support import FIXTURES, make_runner, ok, pass_provider_factory

DIAGRAMS = (
    "/assets/diagrams/lanes.svg",
    "/assets/diagrams/regimes.svg",
    "/assets/diagrams/layers.svg",
    "/assets/diagrams/kit-consumer.svg",
)


def _governance_runner(tmp_path: Path):
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
            "git merge-base --is-ancestor": ok(""),
        }
    )


def test_overview_structure_status_roadmap_actions(tmp_path: Path) -> None:
    artifact = seed_app_e2e_repo(tmp_path)
    rel = artifact.relative_to(tmp_path).as_posix()
    docs = tmp_path / "docs"
    (docs / "OVERSEER-HANDOVER.md").write_text(
        (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    handle, client = start_test_app(
        tmp_path,
        runner=_governance_runner(tmp_path),
        review_provider_factory=pass_provider_factory(),
    )
    try:
        status, health = client.get("/api/health")
        assert status == 200
        assert health["ok"] is True

        request = urllib.request.Request(
            f"{client.base_url}/",
            headers={"Authorization": f"Bearer {client.session}"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            html = response.read().decode("utf-8")
        assert 'id="tab-overview"' in html
        assert 'id="tab-structure"' in html
        for path in DIAGRAMS:
            assert path in html
            svg_req = urllib.request.Request(
                f"{client.base_url}{path}",
                headers={"Authorization": f"Bearer {client.session}"},
            )
            with urllib.request.urlopen(svg_req, timeout=5) as response:
                assert response.status == 200

        _s, status_payload = client.get("/api/status")
        assert status_payload["result"]["initialized"] is True

        _s, roadmap = client.get("/api/docs/roadmap")
        assert roadmap["ok"] is True

        _s, freeze = client.post("/api/review/freeze", {"path": rel, "dry_run": True})
        assert freeze["exit_code"] == 0

        _s, sync = client.post("/api/governance-sync", {"write": False})
        assert sync["exit_code"] == 0
    finally:
        handle.shutdown()


def test_ok_app_sigint_exit_zero(tmp_path: Path) -> None:
    seed_app_repo(tmp_path)
    port = free_port()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(kit_root())
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "cli.main",
            "app",
            "--port",
            str(port),
            "--bind",
            "127.0.0.1",
            "--repo",
            str(tmp_path),
        ],
        cwd=str(tmp_path),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        time.sleep(0.8)
        proc.send_signal(signal.SIGINT)
        code = proc.wait(timeout=5)
        assert code in {0, -2, 130}
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=3)

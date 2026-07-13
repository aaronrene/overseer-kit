"""E2E — Track O / O3 upgrade-regime dry-run + product-contract retarget (§O2.9 e2e)."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from cli.context import CliContext
from cli.footprint import MUSE_BRIDGE_DEPLOY_DEST
from cli.kit_root import kit_root
from cli.main import main
from cli.output import OutputContext
from tests.support import (
    FIXTURES,
    make_runner,
    muse_mirror_status_runner,
    muse_status_runner,
    ok,
    run_cli,
    seed_muse_substrate,
)
from tools.track_o.validate import CONTRACT_REL, RUNBOOK_REL, validate_track_o_pack

KIT_ROOT = Path(__file__).resolve().parents[2]


def _init_muse_only(tmp_path: Path) -> None:
    seed_muse_substrate(tmp_path)
    assert (
        run_cli(
            [
                "init",
                "--from-config",
                str(FIXTURES / "config-muse-only.yaml"),
                "--non-interactive",
            ],
            cwd=tmp_path,
            kit=kit_root(),
            runner=muse_status_runner(tmp_path),
        )
        == 0
    )


def _runner(tmp_path: Path):
    base = muse_mirror_status_runner(tmp_path)
    responses = dict(base.responses)
    responses["git remote get-url origin"] = ok("https://github.com/example/repo.git")
    return make_runner(responses)


def test_dry_run_full_ceremony_report(tmp_path: Path) -> None:
    _init_muse_only(tmp_path)
    buf = StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        ctx = CliContext.create(
            runner=_runner(tmp_path),
            cwd=tmp_path,
            kit=kit_root(),
            output=OutputContext(json_mode=True),
        )
        code = main(
            [
                "upgrade-regime",
                "--from",
                "muse-only",
                "--to",
                "muse+git-mirror",
                "--dry-run",
                "--json",
            ],
            ctx=ctx,
        )
    finally:
        sys.stdout = old
    assert code == 0
    payload = json.loads(buf.getvalue())
    assert payload["dry_run"] is True
    assert payload["start_state"] == "muse-only"
    assert "G1" in payload["gates"]
    assert "G8" in payload["gates"]
    assert payload["live_bridge_invoked"] is False
    assert "Tier 3" in payload["hard_stop_c8"]
    # Default e2e never invokes live bridge; tree unchanged for bridge files
    assert not (tmp_path / MUSE_BRIDGE_DEPLOY_DEST).exists()


def test_git_only_fixture_refused(tmp_path: Path) -> None:
    assert (
        run_cli(
            ["init", "--regime", "git-only", "--non-interactive"],
            cwd=tmp_path,
            kit=kit_root(),
        )
        == 0
    )
    code = run_cli(
        [
            "upgrade-regime",
            "--from",
            "muse-only",
            "--to",
            "muse+git-mirror",
            "--dry-run",
        ],
        cwd=tmp_path,
        kit=kit_root(),
    )
    assert code == 4


def test_product_contract_and_runbook_after_o3() -> None:
    result = validate_track_o_pack(KIT_ROOT)
    assert result.ok, result.errors
    contract = (KIT_ROOT / CONTRACT_REL).read_text(encoding="utf-8")
    assert "ok upgrade-regime" in contract
    assert "PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY" in contract
    assert "deferred to Thinking O2" not in contract
    assert "coming soon / operator-assisted" not in contract
    assert (KIT_ROOT / RUNBOOK_REL).is_file()
    runbook = (KIT_ROOT / RUNBOOK_REL).read_text(encoding="utf-8")
    assert "ok upgrade-regime" in runbook
    assert "C8" in runbook

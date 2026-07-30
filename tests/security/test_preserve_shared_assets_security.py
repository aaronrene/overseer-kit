"""Security — preserve-shared-assets does not leak contents (§PSA.8)."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from cli.context import CliContext
from cli.kit_root import kit_root
from cli.main import main
from cli.output import OutputContext
from tests.support import PILOT, muse_mirror_status_runner, seed_pilot_tree

SECRET_MARKER = "SUPERSECRET_BRIDGE_TOKEN_xyz"


def test_preserve_report_json_omits_file_contents(tmp_path: Path) -> None:
    seed_pilot_tree(
        tmp_path,
        handover_rel="docs/OVERSEER-HANDOVER.md",
        handover_text="# H\n",
        roadmap_rel="docs/ROADMAP.md",
        roadmap_text="# R\n",
    )
    policy = tmp_path / ".overseer" / "policy"
    policy.mkdir(parents=True, exist_ok=True)
    (policy / "tiers.yaml").write_text(f"token: {SECRET_MARKER}\n", encoding="utf-8")

    out = io.StringIO()
    err = io.StringIO()
    ctx = CliContext.create(
        cwd=tmp_path,
        kit=kit_root(),
        output=OutputContext(json_mode=True),
        runner=muse_mirror_status_runner(tmp_path),
    )
    with redirect_stdout(out), redirect_stderr(err):
        code = main(
            [
                "init",
                "--migrate",
                "--force",
                "--preserve-shared-assets",
                "--from-config",
                str(PILOT / "config-scooling.yaml"),
                "--non-interactive",
            ],
            ctx=ctx,
        )
    assert code == 0
    combined = out.getvalue() + err.getvalue()
    assert SECRET_MARKER not in combined
    payload = json.loads(out.getvalue())
    assert SECRET_MARKER not in json.dumps(payload)
    assert ".overseer/policy/tiers.yaml" in payload.get("preserved", [])

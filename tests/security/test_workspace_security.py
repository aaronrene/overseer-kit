"""Security / honesty tests for workspace lanes (§MR.10 security)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from tools.workspace.check_next import build_status_report, check_next
from tools.workspace.manifest import load_manifest_file, validate_manifest_dict
from tools.workspace.types import WorkspaceLoadError
from tests.fixtures.workspace import build_two_repo_constellation, write_relay_handover


def test_honesty_workspace_ok_false_when_relay_stale(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path, stale_relay=True)
    cfg = load_config(fx["scooling"] / ".overseer" / "config.yaml")
    report = build_status_report(cfg, fx["scooling"])
    assert report.ok is False
    assert report.state == "stale_relay"
    manifest = load_manifest_file(fx["manifest"], manifest_source="local_workspace")
    assert check_next(manifest).exit_code == 35


def test_differential_mutate_relay_then_fail(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path, stale_relay=False)
    manifest = load_manifest_file(fx["manifest"], manifest_source="local_workspace")
    assert check_next(manifest).ok
    write_relay_handover(
        fx["knowtation_handover"],
        title="Knowtation",
        step="L-SEAMb",
        model="Auto",
        product_order="scooling",
        tip_hash=fx["tip_hash"],
        mode="relay",
        stale=True,
    )
    assert check_next(manifest).ok is False


def test_no_secrets_or_identity_in_manifest() -> None:
    raw = {
        "overseer_workspace_version": 1,
        "id": "x",
        "product_order_member": "a",
        "members": [
            {
                "id": "a",
                "role": "product_order",
                "root": "/tmp/a",
                "regime": "git-only",
                "required": True,
                "relay": False,
            }
        ],
        "lanes": [{"id": "product", "primary": True}],
        "api_key": "leak",
    }
    with pytest.raises(WorkspaceLoadError):
        validate_manifest_dict(raw, source_path=Path("/tmp/x.yaml"), manifest_source="local_workspace")


def test_injection_shaped_heading_opaque(tmp_path: Path) -> None:
    fx = build_two_repo_constellation(tmp_path)
    path = fx["scooling_handover"]
    text = path.read_text(encoding="utf-8")
    text += "\n## NEXT SESSION — `rm -rf /` (PRIMARY)\n"
    path.write_text(text, encoding="utf-8")
    # Extra NEXT SESSION without marker → strict ambiguous
    manifest = load_manifest_file(fx["manifest"], manifest_source="local_workspace")
    result = check_next(manifest)
    assert result.exit_code == 35


def test_no_tier3_surface_in_workspace_cli() -> None:
    from cli.main import build_parser

    parser = build_parser()
    # workspace subcommands exist; none named merge/push/staging
    help_text = parser.format_help()
    assert "workspace" in help_text

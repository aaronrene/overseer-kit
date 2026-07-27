"""Unit tests for multi-repo workspace lanes (§MR.10 unit)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.workspace.board_names import (
    board_name_violation,
    expected_handover_basename,
    is_bare_legacy_basename,
    repo_slug,
)
from tools.workspace.manifest import expand_root, validate_manifest_dict
from tools.workspace.next_extract import (
    extract_next_blocks,
    legacy_forbidden_archived_headings,
    tip_hash_hex,
)
from tools.workspace.types import WorkspaceLoadError
from tests.fixtures.workspace import build_two_repo_constellation, primary_fence


def test_repo_slug_normalization() -> None:
    assert repo_slug("overseer-kit") == "OVERSEER-KIT"
    assert repo_slug("scooling") == "SCOOLING"
    assert repo_slug("foo__bar!!") == "FOO-BAR"
    assert expected_handover_basename("scooling") == "SCOOLING-OVERSEER-HANDOVER.md"


def test_bare_vs_prefixed_basename_classifier() -> None:
    assert is_bare_legacy_basename("OVERSEER-HANDOVER.md", kind="handover")
    assert is_bare_legacy_basename("roadmap.md", kind="roadmap")
    assert board_name_violation(
        repo_name="knowtation",
        handover_basename="OVERSEER-HANDOVER.md",
        roadmap_basename="ROADMAP.md",
        strict=True,
    )
    assert not board_name_violation(
        repo_name="knowtation",
        handover_basename="KNOWTATION-OVERSEER-HANDOVER.md",
        roadmap_basename="KNOWTATION-ROADMAP.md",
        strict=True,
    )


def test_root_env_and_home_expansion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WS_ROOT", str(tmp_path / "app"))
    assert expand_root("${WS_ROOT}", environ=dict(**{"WS_ROOT": str(tmp_path / "app")})) == str(
        tmp_path / "app"
    )
    assert expand_root("${MISSING:-~/fallback}", home=tmp_path).endswith("fallback")
    assert expand_root("~/proj", home=tmp_path) == str(tmp_path / "proj")


def test_manifest_rejects_bad_cardinality_and_secrets() -> None:
    base = {
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
    }
    validate_manifest_dict(base, source_path=Path("/tmp/ws.yaml"), manifest_source="local_workspace")

    bad = dict(base)
    bad["members"] = list(base["members"]) + [
        {
            "id": "b",
            "role": "product_order",
            "root": "/tmp/b",
            "regime": "git-only",
            "required": True,
            "relay": False,
        }
    ]
    with pytest.raises(WorkspaceLoadError):
        validate_manifest_dict(bad, source_path=Path("/tmp/ws.yaml"), manifest_source="local_workspace")

    secret = dict(base)
    secret["token"] = "supersecret"
    with pytest.raises(WorkspaceLoadError):
        validate_manifest_dict(secret, source_path=Path("/tmp/ws.yaml"), manifest_source="local_workspace")

    identity = dict(base)
    identity["X-User-Id"] = "abc"
    with pytest.raises(WorkspaceLoadError):
        validate_manifest_dict(identity, source_path=Path("/tmp/ws.yaml"), manifest_source="local_workspace")


def test_regime_null_only_when_optional() -> None:
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
            },
            {
                "id": "brain",
                "role": "edge",
                "root": "",
                "regime": None,
                "required": False,
                "relay": False,
            },
        ],
        "lanes": [{"id": "product", "primary": True}],
    }
    validate_manifest_dict(raw, source_path=Path("/tmp/ws.yaml"), manifest_source="local_workspace")
    raw["members"][1]["required"] = True
    with pytest.raises(WorkspaceLoadError):
        validate_manifest_dict(raw, source_path=Path("/tmp/ws.yaml"), manifest_source="local_workspace")


def test_marker_parse_and_tip_hash_lf_normalize() -> None:
    fence = primary_fence(step="K13b", model="Auto", repo="/tmp/r")
    digest = tip_hash_hex(fence)
    assert digest == tip_hash_hex(fence.replace("\n", "\r\n"))
    text = f"""
<!-- overseer:next role=primary lane=product status=live -->
## NEXT SESSION — K13b (PRIMARY)

```
{fence}```

<!-- overseer:next role=archived status=archived -->
## ARCHIVED SESSION — old

<!-- overseer:next role=lane_tip lane=security status=live -->
## LANE TIP — sec (LANE: security)

```
Model: Thinking
Repo: x
Branch: y
Step: SEC
Authority: lane_tip
```
"""
    blocks = extract_next_blocks(text)
    roles = [b.role.value for b in blocks]
    assert roles == ["primary", "archived", "lane_tip"]
    assert blocks[0].step_id == "K13b"
    assert blocks[0].model == "Auto"


def test_forbidden_legacy_archived_heading() -> None:
    text = "## NEXT SESSION — archived L-SEAM Thinking\n"
    hits = legacy_forbidden_archived_headings(text)
    assert hits and "archived" in hits[0][1].lower()


def test_freshness_true_false(tmp_path: Path) -> None:
    from tools.workspace.check_next import check_next
    from tools.workspace.manifest import load_manifest_file

    good = build_two_repo_constellation(tmp_path / "good", stale_relay=False)
    manifest = load_manifest_file(good["manifest"], manifest_source="local_workspace")
    ok = check_next(manifest)
    assert ok.ok and ok.exit_code == 0

    bad = build_two_repo_constellation(tmp_path / "bad", stale_relay=True)
    stale = check_next(load_manifest_file(bad["manifest"], manifest_source="local_workspace"))
    assert not stale.ok and stale.exit_code == 35
    assert stale.state == "stale_relay"


def test_strict_board_names_default_true() -> None:
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
    }
    m = validate_manifest_dict(raw, source_path=Path("/tmp/ws.yaml"), manifest_source="local_workspace")
    assert m.strict_markers is True
    assert m.strict_board_names is True


def test_workspace_config_parse(tmp_path: Path) -> None:
    from adapters.config import load_config

    cfg_path = tmp_path / "config.yaml"
    data = {
        "overseer_config_version": 1,
        "repo": {"name": "demo", "root_relative_docs": "docs"},
        "vcs": {
            "regime": "git-only",
            "canonical": "git",
            "git": {
                "remote": "origin",
                "main_branch": "main",
                "mirror_branch": None,
                "feature_branch_pattern": "feat/{slug}",
            },
            "muse": {"staging_remote": None, "main_branch": None},
        },
        "docs": {
            "handover": "DEMO-OVERSEER-HANDOVER.md",
            "roadmap": "DEMO-ROADMAP.md",
            "coordination": None,
            "standing_decisions": "DEMO-ROADMAP.md",
            "handover_title": "Demo Overseer Handover",
            "roadmap_title": "Demo Roadmap",
        },
        "thresholds": {"realign_max_commits": 50, "drift_warn_only": True},
        "freeze_contract": {
            "enabled": True,
            "reviewer": {
                "mode": "agent",
                "model": "thinking-high",
                "provider": "local",
                "fallback": "human",
            },
            "human_escalation": ["security"],
        },
        "workspace": {"constellation_id": "demo-stack", "manifest": None, "product_order_root": None},
    }
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    cfg = load_config(cfg_path)
    assert cfg.workspace is not None
    assert cfg.workspace.constellation_id == "demo-stack"

"""End-to-end tests for Track P / P-cost (§PC.9)."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import yaml

from cli.context import CliContext
from cli.kit_root import kit_root
from cli.main import main
from cli.output import OutputContext
from tests.fixtures.cost_awareness import seed_cost_e2e_repo
from tests.fixtures.model_routing import write_routing_policy
from tests.support import git_status_runner, make_runner, ok, run_cli


def test_e2e_thinking_freeze_slice_paid_high(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["status", "--json"],
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=git_status_runner(),
                output=OutputContext(json_mode=True),
                kit=kit_root(),
            ),
        )
    assert code == 0
    payload = json.loads(out.getvalue())
    slices = payload["cost_awareness"]["slices"]
    thinking = next(item for item in slices if item["phase_id"] == "Demo Thinking freeze")
    assert thinking["model_tier"] == "deep-reasoning"
    assert thinking["cost_class"] == "high"
    assert thinking["paid_step_before_spend"] is True


def test_e2e_auto_slice_moderate(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["status", "--json"],
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=git_status_runner(),
                output=OutputContext(json_mode=True),
                kit=kit_root(),
            ),
        )
    assert code == 0
    payload = json.loads(out.getvalue())
    slices = payload["cost_awareness"]["slices"]
    auto = next(item for item in slices if item["phase_id"] == "Demo Auto build")
    assert auto["model_tier"] == "standard"
    assert auto["cost_class"] == "moderate"
    assert auto["paid_step_before_spend"] is True


def test_e2e_local_offline_unpaid(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    write_routing_policy(
        tmp_path,
        """
version: 1
defaults:
  model_tier: local-offline
  fallback: [local-offline, standard, human]
routes:
  - id: freeze-thinking
    when: { gate: freeze_review, phase_tier: thinking }
    model_tier: deep-reasoning
    fallback: [deep-reasoning, human]
  - id: auto-build
    when: { phase_tier: auto }
    model_tier: standard
    fallback: [standard, human]
""",
    )
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["status", "--json"],
            ctx=CliContext.create(
                cwd=tmp_path,
                runner=git_status_runner(),
                output=OutputContext(json_mode=True),
                kit=kit_root(),
            ),
        )
    assert code == 0
    payload = json.loads(out.getvalue())
    offline = next(item for item in payload["cost_awareness"]["slices"] if item["phase_id"] == "Demo Offline worker")
    assert offline["model_tier"] == "local-offline"
    assert offline["cost_class"] == "free"
    assert offline["paid_step_before_spend"] is False


def test_e2e_governance_sync_footer(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    runner = make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok("main"),
            "git status --porcelain": ok(""),
            "git rev-parse origin/main": ok("cafebabe"),
            "gh pr list --state merged --limit 5 --json number,title,mergeCommit,mergedAt": ok("[]"),
            "git remote get-url origin": ok("git@github.com:owner/repo.git"),
        }
    )
    out = StringIO()
    with patch("sys.stdout", out):
        code = main(
            ["governance-sync"],
            ctx=CliContext.create(cwd=tmp_path, runner=runner, kit=kit_root()),
        )
    assert code == 0
    assert "cost_awareness:" in out.getvalue()


def test_e2e_git_only_and_muse_regime_identical(tmp_path: Path) -> None:
    seed_cost_e2e_repo(tmp_path)
    from adapters.config import load_config
    from tools.cost_awareness.surface import build_cost_awareness_report

    config_git = load_config(tmp_path / ".overseer" / "config.yaml")
    handover = (tmp_path / "docs" / "OVERSEER-HANDOVER.md").read_text(encoding="utf-8")
    roadmap = (tmp_path / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    git_report = build_cost_awareness_report(
        config_git, tmp_path, kit_root=kit_root(), handover_text=handover, roadmap_text=roadmap
    )

    cfg = tmp_path / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    data["vcs"]["regime"] = "muse+git-mirror"
    data["vcs"]["canonical"] = "muse"
    data["vcs"]["git"]["mirror_branch"] = "muse-mirror"
    data["vcs"]["muse"]["staging_remote"] = "origin"
    data["vcs"]["muse"]["main_branch"] = "main"
    cfg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    config_muse = load_config(cfg)
    muse_report = build_cost_awareness_report(
        config_muse, tmp_path, kit_root=kit_root(), handover_text=handover, roadmap_text=roadmap
    )
    assert git_report.slices == muse_report.slices

"""Unit tests for P-deploy Mode C gate (§PD.9)."""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest
import yaml

from adapters.config import HONESTY_KEYS, load_config
from tests.fixtures.p_deploy import load_p_deploy_entry
from tests.support import seed_honesty_repo
from tools.honesty.status import HonestyStatusOptions, _resolve_mode
from tools.honesty.types import HonestyErrorToken
from tools.honesty.validate import find_matching_deploy_health


def test_require_deploy_health_config_parse(repo_root: Path) -> None:
    seed_honesty_repo(repo_root)
    cfg_path = repo_root / ".overseer" / "config.yaml"
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    assert "require_deploy_health" not in data["honesty"]
    config = load_config(cfg_path)
    assert config.honesty.require_deploy_health == "off"

    for mode in ("off", "warn", "require"):
        data["honesty"]["require_deploy_health"] = mode
        cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
        assert load_config(cfg_path).honesty.require_deploy_health == mode

    data["honesty"]["require_deploy_health"] = "maybe"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(Exception, match="require_deploy_health"):
        load_config(cfg_path)


def test_require_deploy_health_in_honesty_keys() -> None:
    assert "require_deploy_health" in HONESTY_KEYS


def test_honesty_error_token_includes_missing_deploy_health() -> None:
    assert "missing_deploy_health" in get_args(HonestyErrorToken)


def test_find_matching_deploy_health_last_pass_with_artifact() -> None:
    entries = [
        load_p_deploy_entry("verification-test-output-only.json"),
        load_p_deploy_entry("verification-with-deploy-health.json"),
    ]
    winner = find_matching_deploy_health(
        entries,
        phase_id="Track P / P-deploy",
        frozen_spec="docs/archive/phases/PHASE-TRACK-P-P-DEPLOY.md",
    )
    assert winner is not None
    assert winner["round"] == 2
    assert any(a["type"] == "deploy_health" for a in winner["artifacts"])


def test_find_matching_deploy_health_rejects_test_output_only() -> None:
    entries = [load_p_deploy_entry("verification-test-output-only.json")]
    assert (
        find_matching_deploy_health(
            entries,
            phase_id="Track P / P-deploy",
            frozen_spec=None,
        )
        is None
    )


def test_find_matching_deploy_health_rejects_findings_verdict() -> None:
    entries = [load_p_deploy_entry("verification-findings-deploy.json")]
    assert (
        find_matching_deploy_health(
            entries,
            phase_id="Track P / P-deploy",
            frozen_spec=None,
        )
        is None
    )


def test_find_matching_deploy_health_wrong_phase() -> None:
    entries = [load_p_deploy_entry("verification-with-deploy-health.json")]
    assert (
        find_matching_deploy_health(
            entries,
            phase_id="other-phase",
            frozen_spec=None,
        )
        is None
    )


def test_find_matching_deploy_health_wrong_frozen_spec() -> None:
    entries = [load_p_deploy_entry("verification-with-deploy-health.json")]
    assert (
        find_matching_deploy_health(
            entries,
            phase_id="Track P / P-deploy",
            frozen_spec="docs/OTHER.md",
        )
        is None
    )


def test_find_matching_deploy_health_rejects_non_verifier() -> None:
    entry = load_p_deploy_entry("verification-with-deploy-health.json")
    entry["actor_role"] = "producer"
    assert (
        find_matching_deploy_health(
            [entry],
            phase_id="Track P / P-deploy",
            frozen_spec=None,
        )
        is None
    )


def test_resolve_mode_deploy_health_plus_frozen_spec_is_mode_c() -> None:
    mode = _resolve_mode(
        HonestyStatusOptions(
            hook=None,
            artifact=None,
            deploy_health="Track P / P-deploy",
            frozen_spec="docs/archive/phases/PHASE-TRACK-P-P-DEPLOY.md",
        )
    )
    assert mode == "mode_c"


def test_resolve_mode_b_and_c_together_invalid() -> None:
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                verification_evidence="phase",
                deploy_health="phase",
            )
        )
        is None
    )


def test_resolve_mode_frozen_spec_alone_invalid() -> None:
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook=None,
                artifact=None,
                frozen_spec="docs/archive/phases/PHASE-TRACK-P-P-DEPLOY.md",
            )
        )
        is None
    )


def test_resolve_mode_a_plus_deploy_health_invalid() -> None:
    assert (
        _resolve_mode(
            HonestyStatusOptions(
                hook="board_done",
                artifact="artifacts/sample.txt",
                deploy_health="Track P / P-deploy",
            )
        )
        is None
    )

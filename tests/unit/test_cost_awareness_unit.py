"""Unit tests for Track P / P-cost cost awareness (§PC.9)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.kit_root import kit_root
from tests.support import FIXTURES
from tools.cost_awareness.derive import COST_CLASS_ORDER, derive_cost_view
from tools.cost_awareness.normalize import gate_for_phase, normalize_phase_tier
from tools.governance_gates.types import PendingGate
from tools.model_routing.labels import (
    COST_CLASS_VALUES,
    RoutingPolicyError,
    load_model_tier_cost_bands,
    validate_model_tier_entry,
)


def test_cost_class_optional_valid_values() -> None:
    for band in COST_CLASS_VALUES:
        tier_id = validate_model_tier_entry(
            {
                "id": "fast",
                "display": "Fast",
                "meaning": "quick",
                "cost_class": band,
            },
            index=0,
            path="policy/model-labels.yaml",
        )
        assert tier_id == "fast"


def test_cost_class_rejects_unknown_value() -> None:
    with pytest.raises(ConfigError, match="outside frozen vocabulary"):
        validate_model_tier_entry(
            {
                "id": "fast",
                "display": "Fast",
                "meaning": "quick",
                "cost_class": "unknown",
            },
            index=0,
            path="policy/model-labels.yaml",
        )


def test_cost_class_rejects_non_string() -> None:
    with pytest.raises(ConfigError, match="must be a string"):
        validate_model_tier_entry(
            {
                "id": "fast",
                "display": "Fast",
                "meaning": "quick",
                "cost_class": 42,
            },
            index=0,
            path="policy/model-labels.yaml",
        )


def test_cost_class_recognized_key_not_unknown() -> None:
    validate_model_tier_entry(
        {
            "id": "fast",
            "display": "Fast",
            "meaning": "quick",
            "cost_class": "low",
            "cursor_model_hint": "hint",
        },
        index=0,
        path="policy/model-labels.yaml",
    )


def test_cost_class_fail_closed_exit_32(tmp_path: Path) -> None:
    labels = tmp_path / "policy" / "model-labels.yaml"
    labels.parent.mkdir(parents=True)
    labels.write_text(
        yaml.safe_dump(
            {
                "model_tiers": [
                    {
                        "id": "fast",
                        "display": "Fast",
                        "meaning": "quick",
                        "cost_class": "pricey",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    load_model_tier_cost_bands.cache_clear()
    with pytest.raises(RoutingPolicyError) as exc:
        load_model_tier_cost_bands(tmp_path, fail_closed=True)
    assert exc.value.exit_code == 32
    load_model_tier_cost_bands.cache_clear()


def test_paid_derivation_all_bands() -> None:
    bands = {
        "deep-reasoning": "high",
        "standard": "moderate",
        "fast": "low",
        "local-offline": "free",
    }
    assert derive_cost_view("deep-reasoning", bands) == ("high", True)
    assert derive_cost_view("standard", bands) == ("moderate", True)
    assert derive_cost_view("fast", bands) == ("low", True)
    assert derive_cost_view("local-offline", bands) == ("free", False)


def test_paid_derivation_human_unpaid() -> None:
    assert derive_cost_view("human", {}) == ("free", False)


def test_paid_derivation_absent_band_conservative() -> None:
    assert derive_cost_view("standard", {"standard": None}) == ("unknown", True)


def test_cost_class_ordinal_order() -> None:
    assert COST_CLASS_ORDER["free"] < COST_CLASS_ORDER["low"]
    assert COST_CLASS_ORDER["low"] < COST_CLASS_ORDER["moderate"]
    assert COST_CLASS_ORDER["moderate"] < COST_CLASS_ORDER["high"]


def test_cost_awareness_config_defaults() -> None:
    config = load_config(FIXTURES / "config-git-only.yaml")
    assert config.cost_awareness.enabled is False
    assert config.cost_awareness.surfaces == frozenset({"status", "governance-sync"})


def test_cost_awareness_unknown_surface_exit_2(tmp_path: Path) -> None:
    write = FIXTURES / "config-git-only.yaml"
    cfg = tmp_path / "config.yaml"
    data = yaml.safe_load(write.read_text(encoding="utf-8"))
    data["cost_awareness"] = {"enabled": True, "surfaces": ["handover-paste"]}
    cfg.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="status\\|governance-sync"):
        load_config(cfg)


def test_phase_model_label_normalization() -> None:
    label_ids = frozenset({"thinking", "auto"})
    assert normalize_phase_tier("Thinking", label_ids=label_ids) == "thinking"
    assert normalize_phase_tier("Auto", label_ids=label_ids) == "auto"
    assert normalize_phase_tier("Operator + Auto", label_ids=label_ids) is None


def test_pending_gate_mapping() -> None:
    pending = (
        PendingGate(
            gate_id="build_verification",
            phase_id="Demo Auto",
            artifact=None,
            message="msg",
            invoke="invoke",
        ),
        PendingGate(
            gate_id="freeze_review",
            phase_id="Demo Thinking",
            artifact="docs/x.md",
            message="msg",
            invoke="invoke",
        ),
    )
    assert gate_for_phase(pending, "Demo Thinking") == "freeze_review"
    assert gate_for_phase(pending, "Demo Auto") == "build_verification"
    assert gate_for_phase(pending, "Other") is None


def test_derivation_is_pure_no_io() -> None:
    bands = {"standard": "moderate"}
    first = derive_cost_view("standard", bands)
    second = derive_cost_view("standard", bands)
    assert first == second == ("moderate", True)

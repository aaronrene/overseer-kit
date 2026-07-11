"""Unit tests for freeze_contract.reviewer schema (§K5.3)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.config_gen import default_config_dict, load_config_from_dict
from tests.support import FIXTURES, write_config


def test_nested_reviewer_mapping_parses(repo_root: Path) -> None:
    path = write_config(repo_root, "config-git-only.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["freeze_contract"]["reviewer"] = {
        "mode": "agent",
        "model": "thinking-high",
        "provider": "local",
        "fallback": "human",
    }
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    config = load_config(path)
    assert config.freeze_contract.reviewer.mode == "agent"
    assert config.freeze_contract.reviewer.model == "thinking-high"


def test_legacy_string_normalizes(repo_root: Path) -> None:
    config = load_config(write_config(repo_root, "config-git-only.yaml"))
    assert config.freeze_contract.reviewer.mode == "agent"
    assert config.freeze_contract.reviewer.model == "thinking-high"
    assert config.freeze_contract.reviewer.provider == "local"
    assert config.freeze_contract.reviewer.fallback == "human"


def test_unknown_model_label_rejected_via_cli_validation(tmp_path: Path) -> None:
    from cli.kit_root import kit_root
    from tools.freeze_reviewer.labels import validate_reviewer_model

    with pytest.raises(ConfigError, match="unknown reviewer.model"):
        validate_reviewer_model("not-a-real-label", kit_root())


def test_unknown_provider_rejected(repo_root: Path) -> None:
    path = write_config(repo_root, "config-git-only.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["freeze_contract"]["reviewer"] = {
        "mode": "agent",
        "model": "thinking-high",
        "provider": "satellite",
        "fallback": "human",
    }
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="provider"):
        load_config(path)


def test_unknown_escalation_token_rejected(repo_root: Path) -> None:
    path = write_config(repo_root, "config-git-only.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["freeze_contract"]["human_escalation"] = ["bogus"]
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="human_escalation"):
        load_config(path)


def test_extra_reviewer_keys_rejected(repo_root: Path) -> None:
    path = write_config(repo_root, "config-git-only.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["freeze_contract"]["reviewer"] = {
        "mode": "agent",
        "model": "thinking-high",
        "provider": "local",
        "fallback": "human",
        "extra": True,
    }
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown freeze_contract.reviewer keys"):
        load_config(path)


def test_init_emits_nested_reviewer() -> None:
    data = default_config_dict(regime="git-only", repo_name="x", docs_dir="docs")
    reviewer = data["freeze_contract"]["reviewer"]
    assert isinstance(reviewer, dict)
    assert reviewer["mode"] == "agent"

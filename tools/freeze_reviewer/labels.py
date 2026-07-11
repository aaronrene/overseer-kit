"""Reviewer model label registry (§K5.3)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from adapters.errors import ConfigError

VENDOR_SLUG_MARKERS = ("gpt-", "claude-", "composer-", "o1-", "o3-")


@lru_cache(maxsize=4)
def load_reviewer_model_ids(kit_root: Path) -> frozenset[str]:
    """Load allowed ``reviewer_models[].id`` values from kit-carried policy."""
    path = kit_root / "policy" / "model-labels.yaml"
    if not path.is_file():
        raise ConfigError("reviewer model registry missing", str(path))
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("model-labels.yaml root must be a mapping", str(path))
    models = raw.get("reviewer_models")
    if not isinstance(models, list) or not models:
        raise ConfigError("reviewer_models must be a non-empty list", str(path))
    ids: list[str] = []
    for entry in models:
        if not isinstance(entry, dict):
            raise ConfigError("reviewer_models entries must be mappings", str(path))
        model_id = entry.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ConfigError("reviewer_models[].id must be a non-empty string", str(path))
        ids.append(model_id)
    return frozenset(ids)


def is_vendor_slug(model: str) -> bool:
    """Return True when ``model`` looks like a vendor slug rather than a label."""
    lowered = model.lower()
    return any(marker in lowered for marker in VENDOR_SLUG_MARKERS)


def validate_reviewer_model(model: str, kit_root: Path) -> None:
    """Fail closed on vendor slugs or unknown labels."""
    if is_vendor_slug(model):
        raise ConfigError(
            f"reviewer.model must be a label from reviewer_models, not a vendor slug: {model!r}"
        )
    allowed = load_reviewer_model_ids(kit_root)
    if model not in allowed:
        raise ConfigError(
            f"unknown reviewer.model label {model!r} (allowed: {sorted(allowed)})"
        )

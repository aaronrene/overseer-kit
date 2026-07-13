"""``model_tiers`` registry loader and validation (§PR.3)."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from adapters.errors import ConfigError
from tools.freeze_reviewer.labels import is_vendor_slug

KEBAB_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
MODEL_TIER_ENTRY_KEYS = frozenset({"id", "display", "meaning", "cursor_model_hint"})
HUMAN_TIER = "human"


class RoutingPolicyError(Exception):
    """Routing policy load/validation failure with frozen exit codes."""

    def __init__(self, message: str, *, exit_code: int = 30, citation: str | None = None) -> None:
        self.message = message
        self.exit_code = exit_code
        self.citation = citation
        super().__init__(message)


@lru_cache(maxsize=4)
def load_model_tier_ids(kit_root: Path) -> frozenset[str]:
    """Load allowed ``model_tiers[].id`` values from kit-carried policy."""
    path = kit_root / "policy" / "model-labels.yaml"
    if not path.is_file():
        raise ConfigError("model tier registry missing", str(path))
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("model-labels.yaml root must be a mapping", str(path))
    tiers = raw.get("model_tiers")
    if not isinstance(tiers, list) or not tiers:
        raise ConfigError("model_tiers must be a non-empty list", str(path))
    ids: list[str] = []
    for index, entry in enumerate(tiers):
        tier_id = validate_model_tier_entry(entry, index=index, path=str(path))
        ids.append(tier_id)
    if len(ids) != len(set(ids)):
        raise ConfigError("model_tiers[].id values must be unique", str(path))
    return frozenset(ids)


def validate_model_tier_entry(entry: object, *, index: int, path: str) -> str:
    """Validate one ``model_tiers`` entry; return its ``id``."""
    prefix = f"model_tiers[{index}]"
    if not isinstance(entry, dict):
        raise ConfigError(f"{prefix} must be a mapping", path)
    extra = set(entry) - MODEL_TIER_ENTRY_KEYS
    if extra:
        raise ConfigError(f"unknown {prefix} keys: {sorted(extra)}", path)
    tier_id = entry.get("id")
    if not isinstance(tier_id, str) or not tier_id.strip():
        raise ConfigError(f"{prefix}.id must be a non-empty string", path)
    if not KEBAB_ID_RE.match(tier_id):
        raise ConfigError(f"{prefix}.id must be lowercase kebab-case", path)
    if is_vendor_slug(tier_id):
        raise ConfigError(f"{prefix}.id must not be a vendor slug", path)
    for field in ("display", "meaning"):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"{prefix}.{field} must be a non-empty string", path)
    hint = entry.get("cursor_model_hint")
    if hint is not None:
        if not isinstance(hint, str) or not hint.strip():
            raise ConfigError(f"{prefix}.cursor_model_hint must be a non-empty string", path)
        if is_vendor_slug(hint):
            raise ConfigError(f"{prefix}.cursor_model_hint must not contain vendor slugs", path)
    for field in ("display", "meaning"):
        if is_vendor_slug(entry[field]):
            raise ConfigError(f"{prefix}.{field} must not contain vendor slugs", path)
    return tier_id


def validate_model_tiers_document(raw: object, *, path: str) -> frozenset[str]:
    """Validate a full model-labels document's ``model_tiers`` section."""
    if not isinstance(raw, dict):
        raise ConfigError("model-labels.yaml root must be a mapping", path)
    tiers = raw.get("model_tiers")
    if not isinstance(tiers, list) or not tiers:
        raise ConfigError("model_tiers must be a non-empty list", path)
    ids: list[str] = []
    for index, entry in enumerate(tiers):
        ids.append(validate_model_tier_entry(entry, index=index, path=path))
    if len(ids) != len(set(ids)):
        raise ConfigError("model_tiers[].id values must be unique", path)
    return frozenset(ids)


def allowed_model_tier_ids(kit_root: Path) -> frozenset[str]:
    """Return ``model_tiers`` ids plus the reserved ``human`` terminal."""
    return load_model_tier_ids(kit_root) | {HUMAN_TIER}

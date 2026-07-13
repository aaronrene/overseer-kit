"""``model_tiers`` registry loader and validation (§PR.3, §PC.3)."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from adapters.errors import ConfigError
from tools.freeze_reviewer.labels import is_vendor_slug

KEBAB_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
MODEL_TIER_ENTRY_KEYS = frozenset({"id", "display", "meaning", "cursor_model_hint", "cost_class"})
HUMAN_TIER = "human"
COST_CLASS_VALUES = frozenset({"free", "low", "moderate", "high"})


class RoutingPolicyError(Exception):
    """Routing policy load/validation failure with frozen exit codes."""

    def __init__(self, message: str, *, exit_code: int = 30, citation: str | None = None) -> None:
        self.message = message
        self.exit_code = exit_code
        self.citation = citation
        super().__init__(message)


def _validate_cost_class_value(
    value: object,
    *,
    prefix: str,
    path: str,
    fail_closed: bool,
) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        message = f"{prefix}.cost_class must be a string"
        if fail_closed:
            raise RoutingPolicyError(message, exit_code=32, citation=path)
        raise ConfigError(message, path)
    if value not in COST_CLASS_VALUES:
        message = (
            f"{prefix}.cost_class {value!r} outside frozen vocabulary "
            f"{sorted(COST_CLASS_VALUES)}"
        )
        if fail_closed:
            raise RoutingPolicyError(message, exit_code=32, citation=path)
        raise ConfigError(message, path)


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


@lru_cache(maxsize=4)
def load_label_ids(kit_root: Path) -> frozenset[str]:
    """Load ``labels[].id`` values from kit-carried policy."""
    path = kit_root / "policy" / "model-labels.yaml"
    if not path.is_file():
        raise ConfigError("model labels registry missing", str(path))
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("model-labels.yaml root must be a mapping", str(path))
    labels = raw.get("labels")
    if not isinstance(labels, list) or not labels:
        raise ConfigError("labels must be a non-empty list", str(path))
    ids: list[str] = []
    for index, entry in enumerate(labels):
        if not isinstance(entry, dict):
            raise ConfigError(f"labels[{index}] must be a mapping", str(path))
        label_id = entry.get("id")
        if not isinstance(label_id, str) or not label_id.strip():
            raise ConfigError(f"labels[{index}].id must be a non-empty string", str(path))
        ids.append(label_id.strip())
    return frozenset(ids)


@lru_cache(maxsize=4)
def load_model_tier_cost_bands(kit_root: Path, *, fail_closed: bool = False) -> dict[str, str | None]:
    """Load declared ``cost_class`` bands keyed by ``model_tiers[].id``.

    When ``fail_closed`` is True, malformed ``cost_class`` values raise
    ``RoutingPolicyError`` with exit code ``32``.
    """
    path = kit_root / "policy" / "model-labels.yaml"
    citation = str(path)
    if not path.is_file():
        message = "model tier registry missing"
        if fail_closed:
            raise RoutingPolicyError(message, exit_code=32, citation=citation)
        raise ConfigError(message, citation)

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        message = "model-labels.yaml root must be a mapping"
        if fail_closed:
            raise RoutingPolicyError(message, exit_code=32, citation=citation)
        raise ConfigError(message, citation)

    tiers = raw.get("model_tiers")
    if not isinstance(tiers, list) or not tiers:
        message = "model_tiers must be a non-empty list"
        if fail_closed:
            raise RoutingPolicyError(message, exit_code=32, citation=citation)
        raise ConfigError(message, citation)

    bands: dict[str, str | None] = {}
    for index, entry in enumerate(tiers):
        prefix = f"model_tiers[{index}]"
        if not isinstance(entry, dict):
            message = f"{prefix} must be a mapping"
            if fail_closed:
                raise RoutingPolicyError(message, exit_code=32, citation=citation)
            raise ConfigError(message, citation)
        tier_id = entry.get("id")
        if not isinstance(tier_id, str) or not tier_id.strip():
            message = f"{prefix}.id must be a non-empty string"
            if fail_closed:
                raise RoutingPolicyError(message, exit_code=32, citation=citation)
            raise ConfigError(message, citation)
        cost_class = entry.get("cost_class")
        _validate_cost_class_value(
            cost_class,
            prefix=prefix,
            path=citation,
            fail_closed=fail_closed,
        )
        bands[tier_id.strip()] = cost_class if cost_class is not None else None
    return bands


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
    _validate_cost_class_value(
        entry.get("cost_class"),
        prefix=prefix,
        path=path,
        fail_closed=False,
    )
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

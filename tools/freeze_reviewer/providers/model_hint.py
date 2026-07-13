"""Resolve reviewer model labels to provider hints (§K5.3)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from adapters.errors import ConfigError

DEFAULT_KIT_ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=4)
def _load_reviewer_model_hints(kit_root: str) -> dict[str, str]:
    """Load ``reviewer_models[].id`` → ``cursor_model_hint`` from kit policy."""
    root = Path(kit_root)
    path = root / "policy" / "model-labels.yaml"
    if not path.is_file():
        raise ConfigError("reviewer model registry missing", str(path))
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("model-labels.yaml root must be a mapping", str(path))
    models = raw.get("reviewer_models")
    if not isinstance(models, list) or not models:
        raise ConfigError("reviewer_models must be a non-empty list", str(path))
    hints: dict[str, str] = {}
    for entry in models:
        if not isinstance(entry, dict):
            raise ConfigError("reviewer_models entries must be mappings", str(path))
        model_id = entry.get("id")
        hint = entry.get("cursor_model_hint")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ConfigError("reviewer_models[].id must be a non-empty string", str(path))
        if not isinstance(hint, str) or not hint.strip():
            raise ConfigError(
                f"reviewer_models[{model_id!r}].cursor_model_hint must be a non-empty string",
                str(path),
            )
        hints[model_id] = hint.strip()
    return hints


def resolve_model_hint(model_label: str, *, kit_root: Path | None = None) -> str:
    """Return the cursor_model_hint for a reviewer model label."""
    root = kit_root or DEFAULT_KIT_ROOT
    hints = _load_reviewer_model_hints(str(root.resolve()))
    try:
        return hints[model_label]
    except KeyError as exc:
        raise ConfigError(
            f"unknown reviewer.model label {model_label!r} (allowed: {sorted(hints)})"
        ) from exc

"""Built-in freeze reviewer checklist (§K5.5)."""

from __future__ import annotations

from pathlib import Path

import yaml

from adapters.errors import ConfigError
from tools.freeze_reviewer.types import ChecklistItem, Severity

BUILTIN_CHECKLIST: tuple[ChecklistItem, ...] = (
    ChecklistItem("C1", "Ground-truth edge", "MAJOR"),
    ChecklistItem("C2", "Completeness", "BLOCKER"),
    ChecklistItem("C3", "Internal consistency", "MAJOR"),
    ChecklistItem("C4", "Security", "BLOCKER"),
    ChecklistItem("C5", "Irreversibility", "BLOCKER"),
    ChecklistItem("C6", "Real money", "BLOCKER"),
    ChecklistItem("C7", "Tier-3 linkage", "BLOCKER"),
    ChecklistItem("C8", "Citation readiness", "MINOR"),
)

VALID_SEVERITIES = frozenset({"BLOCKER", "MAJOR", "MINOR"})


def builtin_checklist() -> list[ChecklistItem]:
    """Return a copy of the §K5.5 built-in checklist."""
    return list(BUILTIN_CHECKLIST)


def load_checklist_file(path: Path) -> list[ChecklistItem]:
    """Parse and validate an operator ``--checklist`` file."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid checklist YAML: {exc}", str(path)) from exc
    if not isinstance(raw, dict):
        raise ConfigError("checklist root must be a mapping", str(path))
    checks = raw.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ConfigError("checklist checks must be a non-empty list", str(path))
    items: list[ChecklistItem] = []
    for index, entry in enumerate(checks):
        if not isinstance(entry, dict):
            raise ConfigError(f"checks[{index}] must be a mapping", str(path))
        check_id = entry.get("id")
        title = entry.get("title")
        severity = entry.get("typical_severity")
        if not isinstance(check_id, str) or not check_id.strip():
            raise ConfigError(f"checks[{index}].id must be a non-empty string", str(path))
        if not isinstance(title, str) or not title.strip():
            raise ConfigError(f"checks[{index}].title must be a non-empty string", str(path))
        if severity not in VALID_SEVERITIES:
            raise ConfigError(
                f"checks[{index}].typical_severity must be BLOCKER|MAJOR|MINOR",
                str(path),
            )
        items.append(ChecklistItem(check_id, title, severity))  # type: ignore[arg-type]
    return items

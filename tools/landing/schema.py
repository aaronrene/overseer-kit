"""Frozen landing manifest types (K12)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class LandingManifest:
    """Parsed ``docs/landing/manifest.yaml`` contract."""

    version: int
    license: str
    section_ids: tuple[str, ...]
    persona_ids: tuple[str, ...]
    status_badges: frozenset[str]
    funnel_steps: tuple[str, ...]


def load_manifest(manifest_path: Path) -> LandingManifest:
    """Load and normalize the landing manifest."""
    raw: dict[str, Any] = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("manifest root must be a mapping")

    version = raw.get("version")
    if version != 1:
        raise ValueError(f"unsupported manifest version: {version!r}")

    license_id = raw.get("license")
    if not isinstance(license_id, str) or not license_id.strip():
        raise ValueError("manifest.license must be a non-empty string")

    sections = raw.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("manifest.sections must be a non-empty list")
    section_ids: list[str] = []
    for item in sections:
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError("each section must be a mapping with id")
        section_ids.append(str(item["id"]))

    personas = raw.get("personas")
    if not isinstance(personas, list) or not personas:
        raise ValueError("manifest.personas must be a non-empty list")
    persona_ids: list[str] = []
    for item in personas:
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError("each persona must be a mapping with id")
        persona_ids.append(str(item["id"]))
        status = item.get("status")
        if status not in raw.get("status_badges", []):
            raise ValueError(f"persona {item['id']} has unknown status {status!r}")

    badges = raw.get("status_badges")
    if not isinstance(badges, list) or not badges:
        raise ValueError("manifest.status_badges must be a non-empty list")

    funnel = raw.get("funnel_steps")
    if not isinstance(funnel, list) or not funnel:
        raise ValueError("manifest.funnel_steps must be a non-empty list")

    return LandingManifest(
        version=int(version),
        license=license_id.strip(),
        section_ids=tuple(section_ids),
        persona_ids=tuple(persona_ids),
        status_badges=frozenset(str(b) for b in badges),
        funnel_steps=tuple(str(s) for s in funnel),
    )

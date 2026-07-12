"""Injection-safe API review request payloads (§K5.5 / §K5.11)."""

from __future__ import annotations

import json
from typing import Any

from tools.freeze_reviewer.types import ChecklistItem

ARTIFACT_BEGIN = "-----BEGIN OVERSEER FREEZE ARTIFACT (DATA ONLY)-----"
ARTIFACT_END = "-----END OVERSEER FREEZE ARTIFACT (DATA ONLY)-----"
SCHEMA_VERSION = 1


def build_delimited_artifact(artifact_text: str) -> str:
    """Wrap artifact bytes as a clearly delimited data section for provider prompts."""
    return "\n".join([ARTIFACT_BEGIN, artifact_text, ARTIFACT_END])


def build_review_request_body(
    *,
    artifact_text: str,
    artifact_path: str,
    checklist: list[ChecklistItem],
    model_label: str,
    model_hint: str,
) -> dict[str, Any]:
    """Build the JSON body for POST /review (headless provider contract)."""
    return {
        "schema_version": SCHEMA_VERSION,
        "model_label": model_label,
        "model_hint": model_hint,
        "artifact_path": artifact_path,
        "artifact_text": build_delimited_artifact(artifact_text),
        "checklist": [
            {
                "id": item.id,
                "title": item.title,
                "typical_severity": item.typical_severity,
            }
            for item in checklist
        ],
    }


def serialize_review_request(body: dict[str, Any]) -> bytes:
    """Serialize a review request as UTF-8 JSON."""
    return json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

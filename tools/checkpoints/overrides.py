"""Canonical JSON for overrides temp file (§K9.5 step 6c)."""

from __future__ import annotations

import json
from typing import Any


def canonical_overrides_json(data: dict[str, Any]) -> str:
    """Serialize overrides with sorted keys and no insignificant whitespace."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

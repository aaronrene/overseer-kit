"""Step and template id validation (§K9.3)."""

from __future__ import annotations

import re

STEP_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


def is_valid_step_id(value: str) -> bool:
    """Return True when ``value`` matches the frozen id regex."""
    return bool(STEP_ID_PATTERN.match(value))

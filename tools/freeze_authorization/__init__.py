"""Freeze-review Auto authorization (§FRV.6.4)."""

from __future__ import annotations

from tools.freeze_authorization.resolve import (
    ACCEPT_LEGACY_VERDICT_STAMP,
    FreezeAuthorization,
    ResolvedStamp,
    freeze_authorization_state,
    resolve_stamp_record,
)

__all__ = [
    "ACCEPT_LEGACY_VERDICT_STAMP",
    "FreezeAuthorization",
    "ResolvedStamp",
    "freeze_authorization_state",
    "resolve_stamp_record",
]

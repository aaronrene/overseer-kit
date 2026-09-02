"""Reminder tips for optional config features (LT follow-up patch)."""

from __future__ import annotations

from adapters.config import OverseerConfig


def build_optional_feature_tips(config: OverseerConfig) -> list[str]:
    """Return human-readable tips when optional LT features are disabled."""
    tips: list[str] = []
    if not config.session_bookends.enabled:
        tips.append(
            "tip: session_bookends off — set session_bookends.enabled: true in "
            ".overseer/config.yaml then ok sync for Cursor session start/end nudges "
            "(cursor/hooks/README.md)"
        )
    if not config.honesty.enabled:
        tips.append(
            "tip: honesty off — set honesty.enabled: true in .overseer/config.yaml "
            "for verification-evidence reminders (require_verification_evidence: warn|require)"
        )
    return tips


def optional_feature_tips_payload(tips: list[str]) -> dict:
    """JSON payload for ``overseer status --json``."""
    return {"tips": list(tips)}

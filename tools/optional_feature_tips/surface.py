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
            "for verification-evidence and independent-second-reviewer reminders "
            "(require_verification_evidence / require_independent_second_reviewer: warn|require; "
            "docs/INDEPENDENT-SECOND-REVIEWER.md)"
        )
    elif config.honesty.require_independent_second_reviewer == "off":
        tips.append(
            "tip: require_independent_second_reviewer off (opted out) — default is "
            "require; set honesty.require_independent_second_reviewer: require to "
            "re-enable second-chat DONE gating (docs/INDEPENDENT-SECOND-REVIEWER.md)"
        )
    return tips


def optional_feature_tips_payload(tips: list[str]) -> dict:
    """JSON payload for ``overseer status --json``."""
    return {"tips": list(tips)}

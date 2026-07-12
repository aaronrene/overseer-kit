"""Governance gate checklist lines for paste prompts and CLI footers (§KH1.9)."""

from __future__ import annotations

FREEZE_REVIEW_INVOKE = (
    "/freeze-review-loop before Thinking freeze → DONE; "
    "overseer review --freeze when CLI green"
)
BUILD_VERIFICATION_INVOKE = (
    "/build-verification-review after every Auto {step}b before ROADMAP DONE"
)


def governance_gates_checklist_lines(*, remind: bool = True) -> tuple[str, ...]:
    """Return frozen Governance gates checklist lines for handover paste blocks."""
    if not remind:
        return (
            "Governance gates (reminders suppressed — Tier 2 ack; gates still mandatory):",
            f"- Freeze review: {FREEZE_REVIEW_INVOKE}",
            f"- Build verification: {BUILD_VERIFICATION_INVOKE}",
        )
    return (
        "Governance gates (mandatory — remind only; silence is not pass):",
        f"- Freeze review: {FREEZE_REVIEW_INVOKE}",
        f"- Build verification: {BUILD_VERIFICATION_INVOKE}",
    )

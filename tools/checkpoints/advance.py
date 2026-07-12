"""``current_step`` advance rules (§K9.4)."""

from __future__ import annotations


def compute_advance(
    template_steps: list[str],
    verified_step: str,
    steps_verified: dict[str, bool],
    current_step: str,
) -> str:
    """Apply frozen advance rule using post-verify verified flags."""
    if verified_step not in template_steps:
        return current_step
    index = template_steps.index(verified_step)
    for prior_id in template_steps[:index]:
        if not steps_verified.get(prior_id, False):
            return current_step
    if index + 1 < len(template_steps):
        return template_steps[index + 1]
    return verified_step

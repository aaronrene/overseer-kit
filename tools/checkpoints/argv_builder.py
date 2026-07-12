"""Child verify-script argv builder (§K9.5 step 6c)."""

from __future__ import annotations


def build_verify_argv(
    *,
    verify_script: str,
    manifest_rel: str,
    step_id: str,
    policy_rel: str,
) -> list[str]:
    """Build argv for domain verify script — always includes ``--policy``."""
    return [
        verify_script,
        "--manifest",
        manifest_rel,
        "--step",
        step_id,
        "--policy",
        policy_rel,
    ]

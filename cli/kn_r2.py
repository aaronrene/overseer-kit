"""Knowtation KN-R2 rule-fragment semantic parity (§K6.3.2)."""

from __future__ import annotations

import re
from pathlib import Path

from adapters.config import OverseerConfig
from adapters.templating import render_template
from cli.kit_root import kit_root

KN_R2_RULE_REL = "cursor/rules/no-docs-only-pr-to-main.mdc"
KN_R2_DEST = ".cursor/rules/no-docs-only-pr-to-main.mdc"


def render_kn_r2_rule(config: OverseerConfig, *, kit: Path | None = None) -> bytes:
    """Render the kit no-docs-only rule with consumer tokens."""
    root = kit or kit_root()
    path = root / KN_R2_RULE_REL
    return render_template(path, config).encode("utf-8")


def kn_r2_always_apply(text: str) -> bool:
    """Return True when frontmatter sets ``alwaysApply: true``."""
    match = re.search(r"(?mi)^alwaysApply:\s*true\s*$", text)
    return match is not None


def kn_r2_forbids_docs_only_to_main(text: str, main_branch: str) -> bool:
    """Return True when text forbids docs-only PR/merge to ``main_branch``."""
    lowered = text.lower()
    if "docs-only" not in lowered and "docs only" not in lowered:
        return False
    if main_branch.lower() not in lowered and "`main`" not in lowered and " main" not in lowered:
        # Accept hardcoded main even when config branch differs for KN-R3.
        if "main" not in lowered:
            return False
    forbid_markers = ("do **not**", "do not", "forbid", "never open", "never merge", "avoid")
    return any(marker in lowered for marker in forbid_markers)


def kn_r2_allows_feature_branch(text: str) -> bool:
    """Return True when text allows / encourages feature-branch commits."""
    lowered = text.lower()
    return "feature branch" in lowered or "feature-branch" in lowered


def kn_r2_semantic_parity(
    consumer_text: str,
    rendered_kit_text: str,
    *,
    main_branch: str,
) -> bool:
    """KN-R2: semantic parity between consumer rule and rendered kit rule.

    Criteria (frozen): forbids docs-only PR/merge to main branch; allows
    feature-branch commits; ``alwaysApply: true``. Byte-identity is not required.
    """
    for text in (consumer_text, rendered_kit_text):
        if not kn_r2_always_apply(text):
            return False
        if not kn_r2_forbids_docs_only_to_main(text, main_branch):
            return False
        if not kn_r2_allows_feature_branch(text):
            return False
    return True


def evaluate_kn_r2(
    repo_root: Path,
    config: OverseerConfig,
    *,
    kit: Path | None = None,
) -> tuple[bool, bytes, str | None]:
    """Evaluate KN-R2 against on-disk consumer rule.

    Returns ``(pass, rendered_kit_bytes, unified_diff_or_None)``.
    When the destination is absent, returns ``(False, rendered, None)``.
    """
    import difflib

    rendered = render_kn_r2_rule(config, kit=kit)
    dest = repo_root / KN_R2_DEST
    if not dest.is_file():
        return False, rendered, None
    consumer = dest.read_text(encoding="utf-8")
    rendered_text = rendered.decode("utf-8")
    passed = kn_r2_semantic_parity(
        consumer,
        rendered_text,
        main_branch=config.vcs.git.main_branch,
    )
    if passed:
        return True, rendered, None
    diff = "".join(
        difflib.unified_diff(
            consumer.splitlines(keepends=True),
            rendered_text.splitlines(keepends=True),
            fromfile=f"a/{KN_R2_DEST}",
            tofile=f"b/{KN_R2_DEST}",
        )
    )
    return False, rendered, diff

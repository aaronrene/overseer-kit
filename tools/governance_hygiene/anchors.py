"""Named anchor markers for templated section replacement (§4)."""

from __future__ import annotations

import re

ANCHOR_OPEN = "<!-- overseer:anchor:{name} -->"
ANCHOR_CLOSE = "<!-- /overseer:anchor:{name} -->"


def anchor_open(name: str) -> str:
    return ANCHOR_OPEN.format(name=name)


def anchor_close(name: str) -> str:
    return ANCHOR_CLOSE.format(name=name)


HANDOVER_ANCHORS = frozenset(
    {
        "vcs-table",
        "done-recently",
        "verified-snapshot",
        "change-log",
        "next-session",
        "paste-ready-prompt",
    }
)

ROADMAP_ANCHORS = frozenset(
    {
        "build-queue",
        "next-step-glance",
    }
)


def replace_anchor_block(text: str, name: str, new_body: str) -> str:
    """Replace content between named anchors; insert anchors if the block is missing."""
    open_marker = anchor_open(name)
    close_marker = anchor_close(name)
    body = new_body.strip("\n")
    block = f"{open_marker}\n{body}\n{close_marker}"

    pattern = re.compile(
        re.escape(open_marker) + r"\n.*?\n" + re.escape(close_marker),
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(block, text, count=1)

    return _insert_anchor_fallback(text, name, block)


def _insert_anchor_fallback(text: str, name: str, block: str) -> str:
    """Insert anchor block near a known heading when markers are absent."""
    heading_map = {
        "vcs-table": "## VCS (verified",
        "done-recently": "### What just landed",
        "verified-snapshot": "## Verified snapshot",
        "change-log": "## Change log",
        "next-session": "## NEXT SESSION",
        "paste-ready-prompt": "### Paste-ready prompt",
        "build-queue": "## Build queue",
        "next-step-glance": "## Next step at a glance",
    }
    heading = heading_map.get(name)
    if heading and heading in text:
        return text.replace(heading, block + "\n\n" + heading, 1)
    return text.rstrip() + "\n\n" + block + "\n"

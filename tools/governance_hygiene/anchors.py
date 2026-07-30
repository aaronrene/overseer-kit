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
    """Insert or replace anchor block near a known heading when markers are absent.

    ``next-session`` / ``paste-ready-prompt`` use region bounds (§GSP.5.3) so nested
    paste-inside-NEXT dogfood is not swallowed on first regen.
    """
    if name == "next-session":
        replaced = _replace_next_session_region(text, block)
        if replaced is not None:
            return replaced
    if name == "paste-ready-prompt":
        replaced = _replace_paste_ready_region(text, block)
        if replaced is not None:
            return replaced

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


def _replace_next_session_region(text: str, block: str) -> str | None:
    """Replace from ``## NEXT SESSION`` through line before paste heading or snapshot ``---``."""
    lines = text.splitlines(keepends=True)
    start: int | None = None
    end: int | None = None
    for index, line in enumerate(lines):
        if start is None and line.startswith("## NEXT SESSION"):
            start = index
            continue
        if start is None:
            continue
        stripped = line.strip()
        if stripped.startswith("### Paste-ready prompt"):
            end = index
            break
        if stripped == "---":
            # Prefer the --- that precedes ## Verified snapshot when no paste heading.
            ahead = "".join(lines[index + 1 : index + 6])
            if "## Verified snapshot" in ahead or "<!-- overseer:anchor:verified-snapshot" in ahead:
                end = index
                break
    if start is None:
        return None
    if end is None:
        end = len(lines)
    prefix = "".join(lines[:start])
    suffix = "".join(lines[end:])
    body = block if block.endswith("\n") else block + "\n"
    return prefix + body + ("\n" if suffix and not body.endswith("\n\n") else "") + suffix


def _replace_paste_ready_region(text: str, block: str) -> str | None:
    """Replace from ``### Paste-ready prompt`` through the first fenced code block close."""
    lines = text.splitlines(keepends=True)
    start: int | None = None
    fence_open = False
    end: int | None = None
    for index, line in enumerate(lines):
        if start is None:
            if line.strip().startswith("### Paste-ready prompt"):
                start = index
            continue
        stripped = line.strip()
        if not fence_open and stripped.startswith("```"):
            fence_open = True
            continue
        if fence_open and stripped.startswith("```"):
            end = index + 1
            break
    if start is None or end is None:
        return None
    prefix = "".join(lines[:start])
    suffix = "".join(lines[end:])
    body = block if block.endswith("\n") else block + "\n"
    return prefix + body + suffix

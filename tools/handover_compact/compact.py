"""Archive old handover change-log bullets (§LT.6)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from adapters.config import OverseerConfig, resolve_lane_docs

CHANGE_LOG_START = "<!-- overseer:anchor:change-log -->"
CHANGE_LOG_END = "<!-- /overseer:anchor:change-log -->"
DATED_ENTRY_START = re.compile(r"^- \*\*\d{4}-\d{2}-\d{2}\*\*")
POINTER_PREFIX = "- Older entries:"


@dataclass(frozen=True)
class CompactReport:
    ok: bool
    compacted: int
    keep: int
    archive: str
    wrote: bool
    reason: str | None = None


@dataclass(frozen=True)
class _ChangeLogEntry:
    lines: tuple[str, ...]


def compact_handover_change_log(
    config: OverseerConfig,
    repo_root: Path,
    *,
    keep: int,
    write: bool,
    lane: str | None = None,
) -> CompactReport:
    """Compact dated change-log bullets; default dry-run when write is False."""
    lane_docs = resolve_lane_docs(config, lane)
    docs_root = config.repo.root_relative_docs
    handover_rel = f"{docs_root}/{lane_docs.handover}".replace("//", "/")
    handover_path = repo_root / handover_rel
    archive_rel = f"{docs_root}/archive/handover/CHANGE-LOG.md".replace("//", "/")
    archive_path = repo_root / archive_rel

    if not handover_path.is_file():
        return CompactReport(
            ok=False,
            compacted=0,
            keep=keep,
            archive=archive_rel,
            wrote=False,
            reason="change_log_anchor_missing",
        )

    text = handover_path.read_text(encoding="utf-8")
    region = _extract_region(text)
    if region is None:
        return CompactReport(
            ok=False,
            compacted=0,
            keep=keep,
            archive=archive_rel,
            wrote=False,
            reason="change_log_anchor_missing",
        )

    before, region_body, after = region
    entries = _collect_dated_entries(region_body)
    if len(entries) <= keep:
        return CompactReport(
            ok=True,
            compacted=0,
            keep=keep,
            archive=archive_rel,
            wrote=False,
        )

    kept = entries[:keep]
    archived = entries[keep:]
    compacted_count = len(archived)

    kept_text = _render_entries(kept)
    pointer = f"{POINTER_PREFIX} {archive_rel}"
    new_region = kept_text
    if kept_text:
        new_region += "\n\n"
    new_region += pointer + "\n"

    new_handover = before + new_region + after
    archive_block = _render_entries(archived)
    heading = f"## Compacted {date.today().isoformat()}\n\n"
    archive_append = heading + archive_block
    if archive_block and not archive_block.endswith("\n"):
        archive_append += "\n"

    if not write:
        return CompactReport(
            ok=True,
            compacted=compacted_count,
            keep=keep,
            archive=archive_rel,
            wrote=False,
        )

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.is_file():
        existing = archive_path.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
        archive_path.write_text(existing + archive_append, encoding="utf-8")
    else:
        title = f"# Archived handover change log — {config.repo.name}\n\n"
        archive_path.write_text(title + archive_append, encoding="utf-8")

    handover_path.write_text(new_handover, encoding="utf-8")
    return CompactReport(
        ok=True,
        compacted=compacted_count,
        keep=keep,
        archive=archive_rel,
        wrote=True,
    )


def _extract_region(text: str) -> tuple[str, str, str] | None:
    start = text.find(CHANGE_LOG_START)
    end = text.find(CHANGE_LOG_END)
    if start == -1 or end == -1 or end <= start:
        return None
    region_start = start + len(CHANGE_LOG_START)
    before = text[:region_start]
    if before and not before.endswith("\n"):
        before += "\n"
    region_body = text[region_start:end]
    after = text[end:]
    return before, region_body, after


def _collect_dated_entries(region_body: str) -> list[_ChangeLogEntry]:
    entries: list[_ChangeLogEntry] = []
    current: list[str] = []
    for line in region_body.splitlines():
        if line.strip().startswith(POINTER_PREFIX):
            continue
        if DATED_ENTRY_START.match(line):
            if current:
                entries.append(_ChangeLogEntry(lines=tuple(current)))
            current = [line]
        elif current:
            current.append(line)
    if current:
        entries.append(_ChangeLogEntry(lines=tuple(current)))
    return entries


def _render_entries(entries: list[_ChangeLogEntry]) -> str:
    chunks: list[str] = []
    for entry in entries:
        chunk = "\n".join(entry.lines).rstrip()
        if chunk:
            chunks.append(chunk)
    return "\n\n".join(chunks)

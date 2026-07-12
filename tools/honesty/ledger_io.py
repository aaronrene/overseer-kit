"""JSONL ledger IO helpers (§K9.7)."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class LedgerIOError(Exception):
    """Raised when ledger file IO fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def split_jsonl_lines(text: str) -> list[str]:
    """Split JSONL text and ignore a trailing empty segment after final LF."""
    if not text:
        return []
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


def parse_jsonl_text(text: str) -> list[dict[str, Any]]:
    """Parse JSONL records; malformed JSON raises ``ValueError``."""
    records: list[dict[str, Any]] = []
    for index, line in enumerate(split_jsonl_lines(text)):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSONL at line {index + 1}: {exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"ledger line {index + 1} must be a JSON object")
        records.append(obj)
    return records


def read_ledger_entries(path: Path) -> list[dict[str, Any]]:
    """Read ledger entries; missing or empty file returns []."""
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    if not text:
        return []
    return parse_jsonl_text(text)


def serialize_entry(entry: dict[str, Any]) -> str:
    """Serialize one ledger entry as a single JSONL line with trailing LF."""
    return json.dumps(entry, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def atomic_append_lines(path: Path, lines: list[str]) -> None:
    """Append lines atomically; on failure leave prior bytes unchanged."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")

    existing = path.read_text(encoding="utf-8")
    new_content = existing + "".join(lines)
    fd, temp_name = tempfile.mkstemp(prefix=".ledger-", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(new_content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise LedgerIOError(f"ledger write failed: {exc}") from exc

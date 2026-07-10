"""Footprint file classification for ``overseer sync`` (§K4.3)."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from cli.digest import sha256_hex
from cli.footprint import FootprintFile
from cli.version_lock import FootprintEntry, VersionLock


class Classification(str, Enum):
    """Three-way sync classification per §K4.3."""

    UNCHANGED = "unchanged"
    KIT_UPDATED = "kit-updated"
    CONSUMER_MODIFIED = "consumer-modified"
    BOTH_CHANGED = "both-changed"
    MISSING = "missing"


@dataclass(frozen=True)
class ClassifiedFile:
    """One classified footprint file with rendered and on-disk state."""

    destination: str
    source: str
    classification: Classification
    new_content: bytes
    baseline_sha: str | None
    current_sha: str | None

    @property
    def needs_write(self) -> bool:
        return self.classification in {
            Classification.KIT_UPDATED,
            Classification.MISSING,
        }

    @property
    def is_conflict(self) -> bool:
        return self.classification in {
            Classification.CONSUMER_MODIFIED,
            Classification.BOTH_CHANGED,
        }


def matches_glob(destination: str, globs: list[str]) -> bool:
    """Return True when ``destination`` matches any ``--only`` glob."""
    return any(fnmatch.fnmatch(destination, pattern) for pattern in globs)


def classify_footprint(
    rendered: list[FootprintFile],
    lock: VersionLock | None,
    repo_root: Path,
) -> list[ClassifiedFile]:
    """Classify every footprint file using lock baseline and on-disk bytes."""
    baseline = {entry.path: entry for entry in lock.footprint} if lock else {}
    classified: list[ClassifiedFile] = []

    for item in rendered:
        entry = baseline.get(item.destination)
        baseline_sha = entry.sha256 if entry else None
        dest_path = repo_root / item.destination
        if dest_path.is_file():
            current_bytes = dest_path.read_bytes()
            current_sha = sha256_hex(current_bytes)
        else:
            current_bytes = b""
            current_sha = None

        new_sha = sha256_hex(item.content)
        if current_sha is None:
            classification = Classification.MISSING
        elif current_sha == baseline_sha:
            if new_sha == baseline_sha:
                classification = Classification.UNCHANGED
            else:
                classification = Classification.KIT_UPDATED
        elif new_sha == baseline_sha:
            classification = Classification.CONSUMER_MODIFIED
        else:
            classification = Classification.BOTH_CHANGED

        classified.append(
            ClassifiedFile(
                destination=item.destination,
                source=item.source,
                classification=classification,
                new_content=item.content,
                baseline_sha=baseline_sha,
                current_sha=current_sha,
            )
        )

    classified.sort(key=lambda row: row.destination)
    return classified

"""``.overseer/version.lock`` reader/writer per §K4.6 + §K6.4 ``origin``."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from cli.digest import FootprintRecord, compute_footprint_digest, sha256_hex

SUPPORTED_LOCK_VERSION = 1
LOCK_FILENAME = "version.lock"
ORIGIN_KIT = "kit"
ORIGIN_PRESERVED = "preserved"
SUPPORTED_ORIGINS = frozenset({ORIGIN_KIT, ORIGIN_PRESERVED})


@dataclass(frozen=True)
class FootprintEntry:
    """One per-file manifest row in ``version.lock``."""

    path: str
    source: str
    sha256: str
    origin: str = ORIGIN_KIT


@dataclass(frozen=True)
class VersionLock:
    """Parsed ``version.lock`` with full §K4.6 shape + optional ``origin``."""

    lock_version: int
    kit_version: str
    config_version: int
    installed_at: str
    synced_at: str
    footprint_digest: str
    footprint: tuple[FootprintEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a YAML-compatible mapping."""
        footprint_rows: list[dict[str, Any]] = []
        for entry in self.footprint:
            row: dict[str, Any] = {
                "path": entry.path,
                "source": entry.source,
                "sha256": entry.sha256,
            }
            # Omit default kit origin for greenfield lock compatibility; always
            # write preserved (and kit when any preserved exists for clarity).
            if entry.origin != ORIGIN_KIT or any(
                e.origin == ORIGIN_PRESERVED for e in self.footprint
            ):
                row["origin"] = entry.origin
            footprint_rows.append(row)
        return {
            "lock_version": self.lock_version,
            "kit_version": self.kit_version,
            "config_version": self.config_version,
            "installed_at": self.installed_at,
            "synced_at": self.synced_at,
            "footprint_digest": self.footprint_digest,
            "footprint": footprint_rows,
        }


class LockError(Exception):
    """Raised when ``version.lock`` is missing, corrupt, or unsupported."""


def utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 with trailing ``Z``."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def lock_path(repo_root: Path) -> Path:
    """Return the default lock file path."""
    return repo_root / ".overseer" / LOCK_FILENAME


def entry_origin(entry: FootprintEntry | dict[str, Any]) -> str:
    """Return origin for a lock entry; omitted defaults to ``kit`` (§K6.4)."""
    if isinstance(entry, FootprintEntry):
        return entry.origin
    origin = entry.get("origin", ORIGIN_KIT)
    return origin if isinstance(origin, str) else ORIGIN_KIT


def kit_only_records(entries: list[FootprintEntry] | tuple[FootprintEntry, ...]) -> list[FootprintRecord]:
    """Build digest records over ``origin: kit`` (and omitted-default kit) only."""
    records: list[FootprintRecord] = []
    for entry in entries:
        if entry_origin(entry) == ORIGIN_PRESERVED:
            continue
        records.append(FootprintRecord(path=entry.path, sha256_hex=entry.sha256))
    return records


def compute_lock_digest(entries: list[FootprintEntry] | tuple[FootprintEntry, ...]) -> str:
    """Compute ``footprint_digest`` per §K6.4 kit-only rule when preserved exist."""
    has_preserved = any(entry_origin(e) == ORIGIN_PRESERVED for e in entries)
    if has_preserved:
        records = kit_only_records(entries)
    else:
        records = [FootprintRecord(path=e.path, sha256_hex=e.sha256) for e in entries]
    return compute_footprint_digest(records)


def read_version_lock(path: Path) -> VersionLock:
    """Parse and validate ``version.lock``; raise ``LockError`` on violation."""
    if not path.is_file():
        raise LockError("version.lock missing")

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LockError(f"cannot read version.lock: {exc}") from exc

    try:
        raw = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise LockError(f"unparseable version.lock: {exc}") from exc

    if not isinstance(raw, dict):
        raise LockError("version.lock root must be a mapping")

    required_keys = (
        "lock_version",
        "kit_version",
        "config_version",
        "installed_at",
        "synced_at",
        "footprint_digest",
        "footprint",
    )
    missing = [key for key in required_keys if key not in raw]
    if missing:
        raise LockError(f"version.lock missing required key(s): {', '.join(missing)}")

    lock_version = raw["lock_version"]
    if not isinstance(lock_version, int):
        raise LockError("lock_version must be an integer")
    if lock_version != SUPPORTED_LOCK_VERSION:
        raise LockError(
            f"unsupported lock_version {lock_version} (supported: {SUPPORTED_LOCK_VERSION})"
        )

    kit_version = raw["kit_version"]
    if not isinstance(kit_version, str) or not kit_version.strip():
        raise LockError("kit_version must be a non-empty string")

    config_version = raw["config_version"]
    if not isinstance(config_version, int):
        raise LockError("config_version must be an integer")

    installed_at = raw["installed_at"]
    synced_at = raw["synced_at"]
    if not isinstance(installed_at, str) or not isinstance(synced_at, str):
        raise LockError("installed_at and synced_at must be strings")

    footprint_digest = raw["footprint_digest"]
    if not isinstance(footprint_digest, str) or not footprint_digest.startswith("sha256:"):
        raise LockError("footprint_digest must be a sha256: prefixed string")

    footprint_raw = raw["footprint"]
    if not isinstance(footprint_raw, list):
        raise LockError("footprint must be a list")

    entries: list[FootprintEntry] = []
    for item in footprint_raw:
        if not isinstance(item, dict):
            raise LockError("each footprint entry must be a mapping")
        for field in ("path", "source", "sha256"):
            if field not in item or not isinstance(item[field], str):
                raise LockError(f"footprint entry missing or invalid {field}")
        origin = item.get("origin", ORIGIN_KIT)
        if not isinstance(origin, str) or origin not in SUPPORTED_ORIGINS:
            raise LockError(f"footprint entry origin must be kit|preserved, got {origin!r}")
        entries.append(
            FootprintEntry(
                path=item["path"],
                source=item["source"],
                sha256=item["sha256"],
                origin=origin,
            )
        )

    entries.sort(key=lambda e: e.path)
    return VersionLock(
        lock_version=lock_version,
        kit_version=kit_version,
        config_version=config_version,
        installed_at=installed_at,
        synced_at=synced_at,
        footprint_digest=footprint_digest,
        footprint=tuple(entries),
    )


def build_version_lock(
    *,
    kit_version: str,
    config_version: int,
    footprint: list[tuple[str, str, bytes]],
    installed_at: str | None = None,
    synced_at: str | None = None,
    prior_installed_at: str | None = None,
    origins: dict[str, str] | None = None,
) -> VersionLock:
    """Build a new lock from rendered footprint ``(dest_path, source, bytes)`` tuples.

    ``origins`` maps destination path → ``kit|preserved`` (default ``kit``).
    """
    now = utc_now_iso()
    origin_map = origins or {}
    sorted_footprint = sorted(footprint, key=lambda item: item[0])
    entries: list[FootprintEntry] = []
    for dest, source, content in sorted_footprint:
        hex_digest = sha256_hex(content)
        origin = origin_map.get(dest, ORIGIN_KIT)
        if origin not in SUPPORTED_ORIGINS:
            origin = ORIGIN_KIT
        entries.append(
            FootprintEntry(path=dest, source=source, sha256=hex_digest, origin=origin)
        )
    entries_tuple = tuple(entries)
    digest = compute_lock_digest(entries_tuple)
    return VersionLock(
        lock_version=SUPPORTED_LOCK_VERSION,
        kit_version=kit_version,
        config_version=config_version,
        installed_at=prior_installed_at or installed_at or now,
        synced_at=synced_at or now,
        footprint_digest=digest,
        footprint=entries_tuple,
    )


def build_version_lock_from_entries(
    *,
    kit_version: str,
    config_version: int,
    entries: list[FootprintEntry],
    installed_at: str,
    synced_at: str | None = None,
) -> VersionLock:
    """Build a lock from explicit manifest entries (for partial ``--only`` sync)."""
    sorted_entries = sorted(entries, key=lambda e: e.path)
    digest = compute_lock_digest(sorted_entries)
    return VersionLock(
        lock_version=SUPPORTED_LOCK_VERSION,
        kit_version=kit_version,
        config_version=config_version,
        installed_at=installed_at,
        synced_at=synced_at or utc_now_iso(),
        footprint_digest=digest,
        footprint=tuple(sorted_entries),
    )


def write_version_lock(path: Path, lock: VersionLock) -> None:
    """Write ``version.lock`` as YAML."""
    from cli.atomic import atomic_write_text

    text = yaml.safe_dump(
        lock.to_dict(),
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    atomic_write_text(path, text)

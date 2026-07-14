"""Ephemeral in-memory cache of fetched bytes + sha256 (§HGD.4.3).

Never stores secrets. Never authoritative over a fresh upstream response at refresh.
"""

from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CacheEntry:
    """Cached remote bytes with content digest."""

    raw: bytes
    sha256: str
    payload: Any


class EphemeralByteCache:
    """Thread-safe in-memory cache keyed by opaque strings."""

    def __init__(self, *, max_entries: int = 256) -> None:
        self._max = max_entries
        self._lock = threading.Lock()
        self._store: dict[str, CacheEntry] = {}

    @staticmethod
    def digest(raw: bytes) -> str:
        """Return lowercase hex sha256 of ``raw``."""
        return hashlib.sha256(raw).hexdigest()

    def get(self, key: str) -> CacheEntry | None:
        with self._lock:
            return self._store.get(key)

    def put(self, key: str, raw: bytes, payload: Any = None) -> CacheEntry:
        entry = CacheEntry(raw=raw, sha256=self.digest(raw), payload=payload)
        with self._lock:
            if len(self._store) >= self._max and key not in self._store:
                # Drop an arbitrary oldest-ish key (insertion order on 3.7+).
                oldest = next(iter(self._store))
                del self._store[oldest]
            self._store[key] = entry
        return entry

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)

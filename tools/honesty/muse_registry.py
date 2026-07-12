"""Optional Muse agent-key registry seam (§P0.4 / §P0.7).

The kit verifies signatures; Muse owns key custody. Under Muse-backed regimes,
``human_ref`` may resolve via an injected registry in tests or future adapters.
"""

from __future__ import annotations

from typing import Protocol


class MuseAgentKeyRegistry(Protocol):
    """Resolve an agent public key from a human owner reference."""

    def resolve_pubkey(self, *, human_ref: str, agent_id: str) -> str | None:
        """Return ``ed25519:<base64>`` pubkey token or None when unknown."""


class NullMuseAgentKeyRegistry:
    """Default registry: no Muse lookup (entry-embedded pubkey only)."""

    def resolve_pubkey(self, *, human_ref: str, agent_id: str) -> str | None:
        return None

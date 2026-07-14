"""Hosted governance dashboard — read-only remote glance surface (§HGD).

Distinct from Track Q ``tools/app``: remote GitHub/MuseHub read APIs only;
no local engine mutations; no act endpoints.
"""

from __future__ import annotations

__all__ = ["DEFAULT_PORT"]

DEFAULT_PORT = 8766

"""Fail-closed governance freshness gate (§GFG)."""

from tools.governance_freshness.check import (
    GovernanceFreshnessReport,
    check_governance_freshness,
    parse_sync_marker,
)

__all__ = [
    "GovernanceFreshnessReport",
    "check_governance_freshness",
    "parse_sync_marker",
]

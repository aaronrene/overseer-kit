"""Footprint coverage gate — lock must declare every resolve destination (§LT.3.1)."""

from tools.footprint_coverage.check import (
    FootprintCoverageReport,
    check_footprint_coverage,
)

__all__ = ["FootprintCoverageReport", "check_footprint_coverage"]

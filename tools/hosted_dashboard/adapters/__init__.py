"""Adapter package for hosted dashboard remote sources."""

from __future__ import annotations

from tools.hosted_dashboard.adapters.github import GitHubAdapters, MarkerSummary, RepoMeta
from tools.hosted_dashboard.adapters.musehub import MuseHubReadAdapter, musehub_baseline_impossible

__all__ = [
    "GitHubAdapters",
    "MarkerSummary",
    "RepoMeta",
    "MuseHubReadAdapter",
    "musehub_baseline_impossible",
]

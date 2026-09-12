"""Freeze-Step Reviewer engine (SPEC §6, contract §K5 / §FRV)."""

from __future__ import annotations

__all__ = [
    "Finding",
    "ReviewProvider",
    "ReviewResult",
    "Verdict",
    "run_freeze_review",
]


def __getattr__(name: str):
    if name == "run_freeze_review":
        from tools.freeze_reviewer.engine import run_freeze_review

        return run_freeze_review
    if name == "ReviewProvider":
        from tools.freeze_reviewer.providers.base import ReviewProvider

        return ReviewProvider
    if name in {"Finding", "ReviewResult", "Verdict"}:
        from tools.freeze_reviewer import types as _types

        return getattr(_types, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

"""Extract and format the paste-ready fence for ``ok next`` (§ONS.5 / §NXP.3)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tools.governance_hygiene.next_regen import extract_paste_fence_body


# Exact heading — one space before the Unicode em dash (§ONS.5.3).
CURRENT_NEXT_HEADING = "## CURRENT NEXT — paste this"

# Provenance line template — separator is space, U+00B7, space (§NXP.3.2).
PROVENANCE_LINE_TEMPLATE = (
    "**Source:** `{repo_name}` · `{repo_root_abs}` · `{doc_rel}` · lane `{lane}` · read `{read_at}`"
)
PROVENANCE_SEPARATOR = " · "

PASTE_HEADING = "### Paste-ready prompt"

REASON_HANDOVER_MISSING = "handover_missing"
REASON_HANDOVER_UNREADABLE = "handover_unreadable"
REASON_HEADING_MISSING = "heading_missing"
REASON_FENCE_MISSING = "fence_missing"
REASON_FENCE_EMPTY = "fence_empty"
REASON_MODEL_MISSING = "model_missing"
REASON_REPO_ROOT_UNRESOLVED = "repo_root_unresolved"

FAIL_CLOSED_REASONS = frozenset(
    {
        REASON_HANDOVER_MISSING,
        REASON_HANDOVER_UNREADABLE,
        REASON_HEADING_MISSING,
        REASON_FENCE_MISSING,
        REASON_FENCE_EMPTY,
        REASON_MODEL_MISSING,
        REASON_REPO_ROOT_UNRESOLVED,
    }
)

# Injectable clock seam (§NXP.3.4) — production uses real UTC; tests pin.
_Clock = Callable[[], str]
_clock: _Clock | None = None


def utc_read_at() -> str:
    """Return UTC ISO-8601 ``YYYY-MM-DDTHH:MM:SSZ`` at second precision."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def set_read_at_clock(clock: _Clock | None) -> None:
    """Install or clear the injectable ``read_at`` clock (§NXP.3.4)."""
    global _clock
    _clock = clock


def read_at_now() -> str:
    """Return ``read_at`` via the injected clock, else the real UTC clock."""
    if _clock is not None:
        return _clock()
    return utc_read_at()


def absolute_repo_root(repo_root: Path) -> str | None:
    """Return absolute POSIX repo root, or ``None`` when unresolved (§NXP.3.6)."""
    try:
        resolved = repo_root.resolve()
    except (OSError, RuntimeError):
        return None
    if not resolved.is_absolute():
        return None
    return resolved.as_posix()


@dataclass(frozen=True)
class CurrentNextResult:
    """Successful extract of the paste-ready fence body."""

    path: str
    lane: str | None
    fence: str
    heading: str = CURRENT_NEXT_HEADING


@dataclass(frozen=True)
class CurrentNextError:
    """Fail-closed extract outcome (§ONS.5.7 / §NXP.3.6)."""

    reason: str
    detail: str
    path: str | None = None
    lane: str | None = None

    @property
    def message(self) -> str:
        return f"next: {self.reason} — {self.detail}"


def format_provenance_line(
    *,
    repo_name: str | None,
    repo_root_abs: str,
    doc_rel: str,
    lane: str | None,
    read_at: str,
) -> str:
    """Render the single provenance line (§NXP.3.2)."""
    name = (repo_name or "").strip() or "unknown"
    lane_label = lane if lane else "-"
    return PROVENANCE_LINE_TEMPLATE.format(
        repo_name=name,
        repo_root_abs=repo_root_abs,
        doc_rel=doc_rel,
        lane=lane_label,
        read_at=read_at,
    )


def extract_current_next(
    handover_path: Path,
    *,
    repo_relative_path: str,
    lane: str | None,
) -> CurrentNextResult | CurrentNextError:
    """Read ``handover_path`` and return the paste fence or a closed reason.

    Order of fail-closed reasons is frozen (§ONS.5.7). Does not invent a fence
    from roadmap, chat memory, or planned regen bytes.
    """
    if not handover_path.exists():
        return CurrentNextError(
            reason=REASON_HANDOVER_MISSING,
            detail=f"handover not found: {repo_relative_path}",
            path=repo_relative_path,
            lane=lane,
        )

    try:
        text = handover_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return CurrentNextError(
            reason=REASON_HANDOVER_UNREADABLE,
            detail=f"cannot read handover as UTF-8: {exc}",
            path=repo_relative_path,
            lane=lane,
        )

    # Heading check before fence extract so a stray ``` elsewhere cannot win.
    if PASTE_HEADING not in text:
        return CurrentNextError(
            reason=REASON_HEADING_MISSING,
            detail="missing '### Paste-ready prompt' heading (KH1 H7)",
            path=repo_relative_path,
            lane=lane,
        )

    body = extract_paste_fence_body(text)
    if body is None:
        return CurrentNextError(
            reason=REASON_FENCE_MISSING,
            detail="paste-ready heading present but no fenced body",
            path=repo_relative_path,
            lane=lane,
        )

    if not body.strip():
        return CurrentNextError(
            reason=REASON_FENCE_EMPTY,
            detail="paste-ready fence body is empty",
            path=repo_relative_path,
            lane=lane,
        )

    if "Model:" not in body:
        return CurrentNextError(
            reason=REASON_MODEL_MISSING,
            detail="paste-ready fence body lacks 'Model:' (KH1 H8)",
            path=repo_relative_path,
            lane=lane,
        )

    return CurrentNextResult(
        path=repo_relative_path,
        lane=lane,
        fence=body,
        heading=CURRENT_NEXT_HEADING,
    )


def format_current_next(
    result: CurrentNextResult,
    *,
    repo_name: str | None,
    repo_root_abs: str,
    read_at: str,
) -> str:
    """Return human stdout bytes for a successful extract (§NXP.3.1).

    Twelve-step layout (narrow supersede of §ONS.5.4). Trailing newline on the
    last line is included. Fence body bytes are unchanged.
    """
    body = result.fence
    if not body.endswith("\n"):
        body = body + "\n"
    provenance = format_provenance_line(
        repo_name=repo_name,
        repo_root_abs=repo_root_abs,
        doc_rel=result.path,
        lane=result.lane,
        read_at=read_at,
    )
    return f"{CURRENT_NEXT_HEADING}\n\n{provenance}\n\n```text\n{body}```\n"

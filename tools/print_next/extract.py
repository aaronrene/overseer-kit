"""Extract and format the paste-ready fence for ``ok next`` (§ONS.5)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.governance_hygiene.next_regen import extract_paste_fence_body

# Exact heading — one space before the Unicode em dash (§ONS.5.3).
CURRENT_NEXT_HEADING = "## CURRENT NEXT — paste this"

PASTE_HEADING = "### Paste-ready prompt"

REASON_HANDOVER_MISSING = "handover_missing"
REASON_HANDOVER_UNREADABLE = "handover_unreadable"
REASON_HEADING_MISSING = "heading_missing"
REASON_FENCE_MISSING = "fence_missing"
REASON_FENCE_EMPTY = "fence_empty"
REASON_MODEL_MISSING = "model_missing"

FAIL_CLOSED_REASONS = frozenset(
    {
        REASON_HANDOVER_MISSING,
        REASON_HANDOVER_UNREADABLE,
        REASON_HEADING_MISSING,
        REASON_FENCE_MISSING,
        REASON_FENCE_EMPTY,
        REASON_MODEL_MISSING,
    }
)


@dataclass(frozen=True)
class CurrentNextResult:
    """Successful extract of the paste-ready fence body."""

    path: str
    lane: str | None
    fence: str
    heading: str = CURRENT_NEXT_HEADING


@dataclass(frozen=True)
class CurrentNextError:
    """Fail-closed extract outcome (§ONS.5.7)."""

    reason: str
    detail: str
    path: str | None = None
    lane: str | None = None

    @property
    def message(self) -> str:
        return f"next: {self.reason} — {self.detail}"


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


def format_current_next(result: CurrentNextResult) -> str:
    """Return human stdout bytes for a successful extract (§ONS.5.4).

    Trailing newline on the last line is included.
    """
    body = result.fence
    if not body.endswith("\n"):
        body = body + "\n"
    return f"{CURRENT_NEXT_HEADING}\n\n```text\n{body}```\n"

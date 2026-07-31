"""Parse governance doc claims for drift verification (D1/D3)."""

from __future__ import annotations

import re

from tools.governance_hygiene.types import QueueRow

SHA_RE = r"[0-9a-fA-F]{7,40}"
STATUS_RE = r"\*\*([^*]+)\*\*"


def parse_handover_github_main_sha(text: str) -> str | None:
    """Extract claimed GitHub ``main`` sha from handover (D1 left-hand side)."""
    claims: set[str] = set()

    patterns = [
        rf"GitHub\s+`main`\s*\|\s*`?({SHA_RE})`?",
        rf"\*\*main HEAD\*\*\s*\|\s*`({SHA_RE})`",
        rf"\*\*Repo state:\*\*\s*`main`\s+at\s+`({SHA_RE})`",
        rf"GitHub\s+`main`\s*\|\s*`\s*({SHA_RE})\s*`",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            claims.add(match.group(1).lower())

    if not claims:
        return None
    if len(claims) > 1:
        return None
    return next(iter(claims))


def parse_queue_rows(roadmap_text: str) -> list[QueueRow]:
    """Parse build-queue table rows from roadmap (D3 claims)."""
    rows: list[QueueRow] = []
    in_queue = False
    for line in roadmap_text.splitlines():
        if line.strip().startswith("## Build queue"):
            in_queue = True
            continue
        if in_queue and line.startswith("## "):
            break
        if not in_queue or not line.startswith("|"):
            continue
        if "---" in line or "Phase |" in line or "Phase|" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        phase_label = cells[0].strip()
        if not phase_label or phase_label.startswith("<"):
            continue
        rows.append(
            QueueRow(
                phase_label=phase_label,
                model=cells[1].strip(),
                status=cells[2].strip(),
                deliverable=cells[3].strip(),
                raw_line=line,
            )
        )
    return rows


def normalize_status(status: str) -> str:
    """Normalize a queue status cell to uppercase token."""
    cleaned = status.upper()
    for token in ("TODO", "WIP", "DONE", "MERGED", "BLOCKED", "NEXT"):
        if token in cleaned:
            return token
    return cleaned


def phase_tokens(phase_label: str) -> list[str]:
    """Derive searchable tokens from a phase label."""
    tokens: list[str] = []
    bold = re.search(r"\*\*([^*]+)\*\*", phase_label)
    label = bold.group(1) if bold else phase_label
    tokens.append(label.strip())
    for part in re.split(r"[\s/—\-]+", label):
        part = part.strip()
        if part and part not in tokens:
            tokens.append(part)
    return tokens


# Land/PR boilerplate words — never slice-identifying on their own
# (live GSW land-b false-positive: PR "GSW land-b docs sync + …" stamped the
# unrelated open row "PLS-a Post-land main sync freeze" DONE via bare "land"/"sync").
_GENERIC_PHASE_TOKENS = frozenset(
    {
        "main",
        "land",
        "sync",
        "post",
        "docs",
        "doc",
        "fix",
        "freeze",
        "build",
        "mirror",
        "merge",
        "gate",
        "kit",
        "the",
        "and",
        "for",
        "with",
        "review",
    }
)


def pr_matches_row(pr_title: str, row: QueueRow) -> bool:
    """Return whether a merged PR title plausibly belongs to a queue row.

    Only slice-identifying evidence may match: the full phase label as a
    substring, or a word-bounded label token of length >= 3 that is not
    generic land/PR boilerplate (``_GENERIC_PHASE_TOKENS``). Bare fragments
    like ``land`` / ``sync`` / ``a`` must never stamp a queue row.
    """
    title_lower = pr_title.lower()
    tokens = phase_tokens(row.phase_label)
    if not tokens:
        return False
    full_label = tokens[0].lower()
    if full_label and full_label in title_lower:
        return True
    for token in tokens[1:]:
        cleaned = token.lower()
        if len(cleaned) < 3 or cleaned in _GENERIC_PHASE_TOKENS:
            continue
        if re.search(rf"(?<![0-9a-z]){re.escape(cleaned)}(?![0-9a-z])", title_lower):
            return True
    return False

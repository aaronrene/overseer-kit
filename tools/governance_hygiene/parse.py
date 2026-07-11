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


def pr_matches_row(pr_title: str, row: QueueRow) -> bool:
    """Return whether a merged PR title plausibly belongs to a queue row."""
    title_lower = pr_title.lower()
    for token in phase_tokens(row.phase_label):
        if token.lower() in title_lower:
            return True
    return False

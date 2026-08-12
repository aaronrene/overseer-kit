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
        # English product words — live ONS land-b false-positive: PR #63
        # "Contributor prep … visibility checklist" stamped open row
        # "Public repository visibility flip" DONE via bare "visibility".
        "public",
        "repository",
        "visibility",
        "flip",
        "checklist",
        "guide",
        "prep",
    }
)


# Slice IDs only: leading run of UPPERCASE/digits, then one or more hyphen
# segments (PLS-a, GSW-FIX, GFG-D2-FIX, K13-DOGFOOD). Rejects English
# hyphenations like Post-land that appear in titles as "post-land".
_COMPOUND_SLICE_RE = re.compile(r"[A-Z][A-Z0-9]{1,}(?:-[A-Za-z0-9]+)+")


def _compound_slice_ids(phase_label: str) -> list[str]:
    """Hyphenated slice IDs from a phase label (``PLS-a``, ``GSW-FIX``).

    ``phase_tokens`` splits on hyphens, so these must be recovered from the
    full label. Live closeout dogfood: PR #55 title ``queue PLS post-land``
    must not stamp open row ``PLS-a`` via the bare prefix ``PLS``, and must
    not match via the English hyphenation ``Post-land`` / ``post-land``.
    """
    bold = re.search(r"\*\*([^*]+)\*\*", phase_label)
    label = bold.group(1) if bold else phase_label
    return _COMPOUND_SLICE_RE.findall(label)


def _word_bounded(needle: str, haystack: str) -> bool:
    return bool(re.search(rf"(?<![0-9a-z]){re.escape(needle)}(?![0-9a-z])", haystack))


def pr_matches_row(pr_title: str, row: QueueRow) -> bool:
    """Return whether a merged PR title plausibly belongs to a queue row.

    Match evidence, in order:
    1. Full phase label as a substring.
    2. When the label has hyphenated slice IDs (``PLS-a``, ``GSW-FIX``), only
       those compounds may match (word-bounded). Bare prefixes (``PLS``,
       ``GSW``) are not enough — PR titles that merely *mention* a future
       slice must not stamp its open queue row DONE.
    3. Otherwise: word-bounded non-generic tokens of length >= 3.
    """
    title_lower = pr_title.lower()
    tokens = phase_tokens(row.phase_label)
    if not tokens:
        return False
    full_label = tokens[0].lower()
    if full_label and full_label in title_lower:
        return True
    compounds = _compound_slice_ids(row.phase_label)
    if compounds:
        return any(_word_bounded(compound.lower(), title_lower) for compound in compounds)
    for token in tokens[1:]:
        cleaned = token.lower()
        if len(cleaned) < 3 or cleaned in _GENERIC_PHASE_TOKENS:
            continue
        if _word_bounded(cleaned, title_lower):
            return True
    return False

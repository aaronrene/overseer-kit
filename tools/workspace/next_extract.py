"""Parse PRIMARY / RELAY / PRODUCT RELAY / ARCHIVED / LANE TIP markers (§MR.6)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import replace

from tools.workspace.types import NextBlock, NextRole

_MARKER_RE = re.compile(
    r"<!--\s*overseer:next\s+"
    r"role=(?P<role>primary|relay|product_relay|lane_tip|archived)"
    r"(?:\s+lane=(?P<lane>[^\s>]+))?"
    r"(?:\s+status=(?P<status>live|archived))?"
    r"(?:\s+product_order=(?P<product_order>[^\s>]+))?"
    r"(?:\s+tip_hash=sha256:(?P<tip_hash>[0-9a-fA-F]{64}))?"
    r"\s*-->",
    re.IGNORECASE,
)

_HEADING_NEXT = re.compile(r"^##\s+NEXT SESSION\s+[—\-]\s+(?P<title>.+?)\s*$")
_HEADING_PRODUCT_RELAY = re.compile(r"^##\s+PRODUCT RELAY\s+[—\-]\s+(?P<title>.+?)\s*$")
_HEADING_LANE_TIP = re.compile(r"^##\s+LANE TIP\s+[—\-]\s+(?P<title>.+?)\s*$")
_HEADING_ARCHIVED = re.compile(r"^##\s+ARCHIVED SESSION\s+[—\-]\s+(?P<title>.+?)\s*$")

_FENCE_RE = re.compile(r"```(?:[^\n]*)\n(.*?)```", re.DOTALL)
_STEP_RE = re.compile(r"(?im)^\s*Step:\s*(?P<v>.+?)\s*$")
_MODEL_RE = re.compile(r"(?im)^\s*Model:\s*(?P<v>.+?)\s*$")
_AUTHORITY_RE = re.compile(r"(?im)^\s*Authority:\s*(?P<v>.+?)\s*$")
_ID_ROW_RE = re.compile(
    r"(?im)^\|\s*\*?\*?ID\*?\*?\s*\|\s*\*?\*?(?P<id>[^*|\s][^*|]*)\*?\*?\s*\|"
)


def lf_normalize(text: str) -> str:
    """Normalize newlines to LF for stable hashing."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def tip_hash_hex(fence_bytes_text: str) -> str:
    """SHA-256 hex of LF-normalized UTF-8 paste-fence body (§MR.5.1)."""
    normalized = lf_normalize(fence_bytes_text).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def normalize_model_display(label: str) -> str | None:
    """Map fence Model line to canonical display label from policy."""
    cleaned = label.strip().strip("*").strip()
    if not cleaned:
        return None
    mapping = {
        "thinking": "Thinking",
        "auto": "Auto",
        "thinking → auto": "Thinking → Auto",
        "thinking->auto": "Thinking → Auto",
        "thinking_to_auto": "Thinking → Auto",
        "operator + auto": "Operator + Auto",
        "operator_plus_auto": "Operator + Auto",
        "operator+auto": "Operator + Auto",
    }
    lowered = cleaned.lower().replace("—", "→").replace("–", "→")
    lowered = re.sub(r"\s+", " ", lowered)
    if cleaned in {"Thinking", "Auto", "Thinking → Auto", "Operator + Auto"}:
        return cleaned
    return mapping.get(lowered)


def _extract_fence_fields(fence: str | None) -> tuple[str | None, str | None, str | None]:
    if not fence:
        return None, None, None
    step_m = _STEP_RE.search(fence)
    model_m = _MODEL_RE.search(fence)
    auth_m = _AUTHORITY_RE.search(fence)
    step = step_m.group("v").strip() if step_m else None
    model_raw = model_m.group("v").strip() if model_m else None
    model = normalize_model_display(model_raw) if model_raw else None
    authority = auth_m.group("v").strip().lower() if auth_m else None
    return step, model, authority


def _step_from_body(body: str, fence_step: str | None) -> str | None:
    if fence_step:
        return fence_step
    id_m = _ID_ROW_RE.search(body)
    if id_m:
        return id_m.group("id").strip()
    return None


def _forbidden_archived_next_title(title: str) -> bool:
    return "archived" in title.lower()


def _ambiguous_primary_phrase(title: str) -> bool:
    lowered = title.lower()
    return "primary relay" in lowered or "primary (relay)" in lowered


def extract_next_blocks(text: str) -> list[NextBlock]:
    """Extract all marked (and legacy unmarked NEXT) blocks from handover text."""
    lines = lf_normalize(text).split("\n")
    blocks: list[NextBlock] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        marker_m = _MARKER_RE.search(line.strip())
        if marker_m and i + 1 < len(lines):
            heading_line = i + 2  # 1-indexed heading
            heading = lines[i + 1]
            role = NextRole(marker_m.group("role").lower())
            lane = marker_m.group("lane")
            status = (marker_m.group("status") or ("archived" if role is NextRole.ARCHIVED else "live")).lower()
            product_order = marker_m.group("product_order")
            tip_hash = marker_m.group("tip_hash")
            if tip_hash:
                tip_hash = tip_hash.lower()

            # Collect body until next marker or next major heading at ## level that starts a session block
            j = i + 2
            body_lines: list[str] = []
            while j < len(lines):
                peek = lines[j].strip()
                if _MARKER_RE.search(peek):
                    break
                if (
                    _HEADING_NEXT.match(lines[j])
                    or _HEADING_PRODUCT_RELAY.match(lines[j])
                    or _HEADING_LANE_TIP.match(lines[j])
                    or _HEADING_ARCHIVED.match(lines[j])
                ):
                    # Unmarked heading — stop before it so legacy scanner can see it
                    break
                body_lines.append(lines[j])
                j += 1
            body = "\n".join(body_lines)
            fence_m = _FENCE_RE.search(body)
            fence = fence_m.group(1) if fence_m else None
            step, model, authority = _extract_fence_fields(fence)
            step = _step_from_body(body, step)
            blocks.append(
                NextBlock(
                    role=role,
                    lane=lane,
                    status=status,
                    product_order=product_order,
                    tip_hash=tip_hash,
                    heading=heading.strip(),
                    heading_line=heading_line,
                    body=body,
                    fence=fence,
                    step_id=step,
                    model=model,
                    authority=authority,
                    unmarked=False,
                )
            )
            i = j
            continue

        # Legacy / unmarked NEXT SESSION headings
        next_m = _HEADING_NEXT.match(line)
        if next_m:
            # Skip if previous non-empty line was a marker (already consumed)
            title = next_m.group("title")
            j = i + 1
            body_lines = []
            while j < len(lines):
                peek = lines[j].strip()
                if _MARKER_RE.search(peek):
                    break
                if (
                    _HEADING_NEXT.match(lines[j])
                    or _HEADING_PRODUCT_RELAY.match(lines[j])
                    or _HEADING_LANE_TIP.match(lines[j])
                    or _HEADING_ARCHIVED.match(lines[j])
                ):
                    break
                body_lines.append(lines[j])
                j += 1
            body = "\n".join(body_lines)
            fence_m = _FENCE_RE.search(body)
            fence = fence_m.group(1) if fence_m else None
            step, model, authority = _extract_fence_fields(fence)
            step = _step_from_body(body, step)
            blocks.append(
                NextBlock(
                    role=NextRole.PRIMARY,
                    lane=None,
                    status="live",
                    product_order=None,
                    tip_hash=None,
                    heading=line.strip(),
                    heading_line=i + 1,
                    body=body,
                    fence=fence,
                    step_id=step,
                    model=model,
                    authority=authority,
                    unmarked=True,
                )
            )
            i = j
            continue
        i += 1
    return blocks


def legacy_forbidden_archived_headings(text: str) -> list[tuple[int, str]]:
    """Return (line, heading) for ``## NEXT SESSION — … archived …`` (forbidden)."""
    out: list[tuple[int, str]] = []
    for idx, line in enumerate(lf_normalize(text).split("\n"), start=1):
        m = _HEADING_NEXT.match(line)
        if m and _forbidden_archived_next_title(m.group("title")):
            out.append((idx, line.strip()))
    return out


def select_live_primary(blocks: list[NextBlock], *, lane: str = "product") -> NextBlock | None:
    """Select LIVE PRIMARY for a lane (ignores archived)."""
    live = [
        b
        for b in blocks
        if b.role is NextRole.PRIMARY
        and b.status == "live"
        and not b.unmarked
        and (b.lane is None or b.lane == lane)
    ]
    if len(live) == 1:
        return live[0]
    if len(live) > 1:
        return None  # ambiguous — caller treats as ambiguous_primary
    return None


def select_product_tip(blocks: list[NextBlock], *, lane: str = "product") -> tuple[NextBlock | None, str | None]:
    """Select relay XOR product_relay tip for product lane.

    Returns ``(block, error_code)`` where error_code is ``ambiguous_primary`` when both present.
    """
    relays = [
        b
        for b in blocks
        if b.role is NextRole.RELAY
        and b.status == "live"
        and (b.lane is None or b.lane == lane)
    ]
    product_relays = [
        b
        for b in blocks
        if b.role is NextRole.PRODUCT_RELAY
        and b.status == "live"
        and (b.lane is None or b.lane == lane or b.lane == "product")
    ]
    if relays and product_relays:
        return None, "ambiguous_primary"
    if len(relays) > 1 or len(product_relays) > 1:
        return None, "ambiguous_primary"
    if len(relays) == 1:
        return relays[0], None
    if len(product_relays) == 1:
        return product_relays[0], None
    return None, None


def primary_paste_hash(block: NextBlock) -> str | None:
    """Hash of PRIMARY paste fence bytes (required for tip freshness)."""
    if not block.fence:
        return None
    return tip_hash_hex(block.fence)


def heading_role_mismatch(block: NextBlock) -> str | None:
    """Return a short reason when heading pattern disagrees with marker role."""
    heading = block.heading
    if block.role is NextRole.PRIMARY:
        if not heading.startswith("## NEXT SESSION"):
            return "primary marker requires ## NEXT SESSION heading"
        if "(PRIMARY)" not in heading:
            return "PRIMARY heading must end with (PRIMARY)"
        title = heading.split("—", 1)[-1] if "—" in heading else heading.split("-", 1)[-1]
        if _forbidden_archived_next_title(title) or _ambiguous_primary_phrase(title):
            return "forbidden PRIMARY title phrasing"
    elif block.role is NextRole.RELAY:
        if not heading.startswith("## NEXT SESSION"):
            return "relay marker requires ## NEXT SESSION heading"
        if "(RELAY →" not in heading and "(RELAY->" not in heading:
            return "RELAY heading must contain (RELAY → …)"
        title = heading.split("—", 1)[-1] if "—" in heading else heading
        if _forbidden_archived_next_title(title):
            return "forbidden RELAY title with archived"
    elif block.role is NextRole.PRODUCT_RELAY:
        if not heading.startswith("## PRODUCT RELAY"):
            return "product_relay marker requires ## PRODUCT RELAY heading"
    elif block.role is NextRole.LANE_TIP:
        if not heading.startswith("## LANE TIP"):
            return "lane_tip marker requires ## LANE TIP heading"
    elif block.role is NextRole.ARCHIVED:
        if heading.startswith("## NEXT SESSION"):
            return "archived must not use ## NEXT SESSION heading"
        if not heading.startswith("## ARCHIVED SESSION"):
            return "archived marker requires ## ARCHIVED SESSION heading"
    return None


def count_next_session_headings(text: str) -> int:
    """Count ``## NEXT SESSION —`` headings (KH1 H2 / H13)."""
    count = 0
    for line in lf_normalize(text).split("\n"):
        if _HEADING_NEXT.match(line):
            count += 1
    return count


def with_computed_hash(block: NextBlock) -> NextBlock:
    """Return block with tip_hash filled from fence when role is primary."""
    if block.role is NextRole.PRIMARY and block.fence and not block.tip_hash:
        return replace(block, tip_hash=tip_hash_hex(block.fence))
    return block

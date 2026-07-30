"""NEXT SESSION + paste-ready regeneration for governance-sync (§GSP)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from adapters.config import OverseerConfig
from cli.docs_paths import join_docs_rel
from tools.governance_hygiene.parse import normalize_status, parse_queue_rows, phase_tokens
from tools.governance_hygiene.types import QueueRow

# Closed vocabulary from policy/model-labels.yaml ``labels[].display`` (frozen for GS-PASTE).
MODEL_DISPLAY_LABELS = frozenset(
    {
        "Thinking",
        "Auto",
        "Thinking → Auto",
        "Operator + Auto",
    }
)

SPLIT_MODEL = "Thinking → Auto"
REASON_ZERO = "zero_open_rows"
REASON_MULTIPLE = "multiple_open_rows"
REASON_INVALID_MODEL = "invalid_model_label"
REASON_SPLIT = "split_undetermined"
REASON_WORKSPACE_MARKER = "workspace_marker_absent"

OPEN_STATUSES = frozenset({"TODO", "NEXT", "WIP"})
DONE_STATUSES = frozenset({"DONE", "MERGED"})

NEXT_MARKER_RE = re.compile(
    r"<!--\s*overseer:next\s+role=[^>]+-->",
    re.IGNORECASE,
)

HARD_STOPS = (
    "No merge to `main` without Tier 3 · no secrets · no live posture flips · "
    "no inventing NEXT when ambiguous"
)

BUILD_VERIFICATION_LINES = (
    "Governance gates (mandatory — remind only; silence is not pass):",
    "- Freeze review: /freeze-review-loop before Thinking freeze → DONE; "
    "ok review --freeze when CLI green",
    "- Build verification: /build-verification-review after every Auto "
    "{step}b before ROADMAP DONE",
)


@dataclass(frozen=True)
class NextRegenDecision:
    """Outcome of unambiguous-NEXT selection + emission planning."""

    row: QueueRow | None
    reason: str | None
    emit_model: str | None
    step_label: str | None
    is_step_b: bool


def normalize_model_cell(model: str) -> str:
    """Strip surrounding markdown bold from a queue Model cell."""
    text = model.strip()
    if text.startswith("**") and text.endswith("**") and len(text) > 4:
        text = text[2:-2].strip()
    return text


def compact_step_id(phase_label: str) -> str:
    """Primary phase id token (first whitespace-/ segment of bold label)."""
    tokens = phase_tokens(phase_label)
    if not tokens:
        return phase_label.strip()
    primary = tokens[0]
    first = re.split(r"[\s/]+", primary, maxsplit=1)[0].strip()
    return first or primary.strip()


def select_unambiguous_next_row(
    roadmap_text: str,
) -> tuple[QueueRow | None, str | None]:
    """Return the sole open queue row, or ``(None, reason)`` when ambiguous.

    Reasons: ``zero_open_rows`` | ``multiple_open_rows`` | ``invalid_model_label``.
    Split detection is separate (§GSP.5.2) and may add ``split_undetermined``.
    """
    rows = parse_queue_rows(roadmap_text)
    open_rows = [row for row in rows if normalize_status(row.status) in OPEN_STATUSES]
    if len(open_rows) == 0:
        return None, REASON_ZERO
    if len(open_rows) > 1:
        return None, REASON_MULTIPLE
    row = open_rows[0]
    model = normalize_model_cell(row.model)
    if not model or model not in MODEL_DISPLAY_LABELS:
        return None, REASON_INVALID_MODEL
    return row, None


def last_done_row(roadmap_text: str) -> QueueRow | None:
    """Last DONE/MERGED queue row by table order, or None."""
    done: QueueRow | None = None
    for row in parse_queue_rows(roadmap_text):
        if normalize_status(row.status) in DONE_STATUSES:
            done = row
    return done


def _freeze_pass_state(path: Path) -> str:
    """Return ``pass``, ``non_pass``, or ``absent`` for a freeze artifact."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return "absent"

    # YAML fence blocks (primary): look for review_stamp.verdict
    for match in re.finditer(r"```ya?ml\s*\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE):
        try:
            raw = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            continue
        if not isinstance(raw, dict):
            continue
        stamp = raw.get("review_stamp")
        if isinstance(stamp, dict) and "verdict" in stamp:
            verdict = str(stamp.get("verdict", "")).strip().lower()
            return "pass" if verdict == "pass" else "non_pass"

    # Review record prose / table fallback
    if re.search(r"verdict:\s*pass\b", text, flags=re.IGNORECASE):
        return "pass"
    if re.search(
        r"\*\*`?pass`?\*\*|→\s*\*\*`?pass`?\*\*|reviewed\s*→\s*`?pass`?",
        text,
        flags=re.IGNORECASE,
    ):
        return "pass"
    if re.search(r"review_stamp:[\s\S]*?verdict:\s*\S+", text, flags=re.IGNORECASE):
        stamp_match = re.search(
            r"review_stamp:[\s\S]*?verdict:\s*(\S+)",
            text,
            flags=re.IGNORECASE,
        )
        if stamp_match:
            verdict = stamp_match.group(1).strip().strip("'\"`").lower()
            if verdict == "pass":
                return "pass"
            if verdict:
                return "non_pass"
    return "absent"


def _path_under_docs(repo_root: Path, candidate: Path) -> Path | None:
    """Return resolved path if it stays under ``repo_root/docs``; else None."""
    docs = (repo_root / "docs").resolve()
    try:
        resolved = candidate.resolve()
        resolved.relative_to(docs)
    except (OSError, ValueError):
        return None
    if not resolved.is_file():
        return None
    return resolved


def discover_freeze_candidates(
    repo_root: Path,
    step_id: str,
    deliverable: str,
) -> list[Path]:
    """Basename-only freeze discovery under ``docs/`` (§GSP.5.2 / §GSP.9)."""
    docs = repo_root / "docs"
    if not docs.is_dir():
        return []

    tokens: set[str] = set()
    compact = step_id.strip()
    if compact:
        tokens.add(compact)
        base = re.sub(r"-[ab]$", "", compact, flags=re.IGNORECASE)
        if base:
            tokens.add(base)

    found: list[Path] = []
    seen: set[Path] = set()
    # Cap: only top-level docs/*.md names (no recursive walk).
    for path in sorted(docs.glob("*.md")):
        name_lower = path.name.lower()
        if not name_lower.startswith("phase-"):
            continue
        for token in tokens:
            if token.lower() in name_lower:
                resolved = _path_under_docs(repo_root, path)
                if resolved is not None and resolved not in seen:
                    seen.add(resolved)
                    found.append(resolved)
                break

    # Deliverable-cited path under docs/
    for match in re.finditer(r"`?(docs/[^`\s|]+\.md)`?", deliverable):
        rel = match.group(1)
        if ".." in Path(rel).parts:
            continue
        candidate = repo_root / rel
        resolved = _path_under_docs(repo_root, candidate)
        if resolved is not None and resolved not in seen:
            seen.add(resolved)
            found.append(resolved)

    return found


def decide_split_emission(
    row: QueueRow,
    repo_root: Path,
) -> tuple[str | None, str | None, bool]:
    """Return ``(emit_model, reason_or_None, is_step_b)`` for the open row.

    For non-split labels, emit the queue model as a single prompt.
    For ``Thinking → Auto``, emit a or b per freeze-pass detector.
    """
    model = normalize_model_cell(row.model)
    if model != SPLIT_MODEL:
        return model, None, False

    step_id = compact_step_id(row.phase_label)
    candidates = discover_freeze_candidates(repo_root, step_id, row.deliverable)
    if not candidates:
        return "Thinking", None, False

    states = [_freeze_pass_state(path) for path in candidates]
    has_pass = any(state == "pass" for state in states)
    has_non_pass = any(state == "non_pass" for state in states)
    if has_pass and has_non_pass:
        return None, REASON_SPLIT, False
    if has_pass and normalize_status(row.status) in OPEN_STATUSES:
        return "Auto", None, True
    return "Thinking", None, False


def check_workspace_next_marker(
    handover_text: str,
    config: OverseerConfig,
) -> str | None:
    """Return ambiguity reason when workspace is set and NEXT marker is absent."""
    if config.workspace is None:
        return None
    if NEXT_MARKER_RE.search(handover_text):
        return None
    return REASON_WORKSPACE_MARKER


def plan_next_regen(
    *,
    roadmap_text: str,
    handover_text: str,
    config: OverseerConfig,
    repo_root: Path,
) -> NextRegenDecision:
    """Full §GSP.4 + §GSP.5.2 + §GSP.5.4 decision for NEXT/paste regen."""
    row, reason = select_unambiguous_next_row(roadmap_text)
    if row is None:
        return NextRegenDecision(None, reason, None, None, False)

    marker_reason = check_workspace_next_marker(handover_text, config)
    if marker_reason:
        return NextRegenDecision(None, marker_reason, None, None, False)

    emit_model, split_reason, is_step_b = decide_split_emission(row, repo_root)
    if split_reason:
        return NextRegenDecision(None, split_reason, None, None, False)

    step_id = compact_step_id(row.phase_label)
    if normalize_model_cell(row.model) == SPLIT_MODEL:
        step_label = f"{re.sub(r'-[ab]$', '', step_id, flags=re.IGNORECASE)}-{'b' if is_step_b else 'a'}"
    else:
        step_label = step_id

    return NextRegenDecision(row, None, emit_model, step_label, is_step_b)


def _branch_value(config: OverseerConfig, phase_id: str) -> str:
    pattern = config.vcs.git.feature_branch_pattern
    if not pattern or "{slug}" not in pattern:
        return "`unknown`"
    slug = re.sub(r"[^a-z0-9]+", "-", phase_id.lower()).strip("-")
    if not slug:
        return "`unknown`"
    return f"`{pattern.replace('{slug}', slug)}`"


def _docs_read_first(config: OverseerConfig) -> str:
    roadmap = join_docs_rel(config.repo.root_relative_docs, config.docs.roadmap)
    handover = join_docs_rel(config.repo.root_relative_docs, config.docs.handover)
    return f"`{roadmap}`; `{handover}`"


def _landed_table_row(roadmap_text: str) -> str:
    done = last_done_row(roadmap_text)
    if done is None:
        return "| _(none)_ | Queue has no DONE/MERGED row yet |"
    slice_id = compact_step_id(done.phase_label)
    deliverable = done.deliverable.strip() or "_(no deliverable)_"
    return f"| **{slice_id}** | {deliverable} |"


def _current_position(roadmap_text: str, open_row: QueueRow) -> str:
    done = last_done_row(roadmap_text)
    open_id = compact_step_id(open_row.phase_label)
    if done is None:
        return f"→ {open_id}"
    return f"{compact_step_id(done.phase_label)} → {open_id}"


def ensure_primary_next_marker(handover_text: str, config: OverseerConfig) -> str:
    """Insert PRIMARY next marker above NEXT SESSION when absent and allowed."""
    if NEXT_MARKER_RE.search(handover_text):
        return handover_text
    if config.workspace is not None:
        return handover_text
    marker = "<!-- overseer:next role=primary lane=product status=live -->"
    heading = "## NEXT SESSION"
    if heading not in handover_text:
        return handover_text
    return handover_text.replace(heading, f"{marker}\n{heading}", 1)


def render_next_session(
    *,
    decision: NextRegenDecision,
    roadmap_text: str,
    config: OverseerConfig,
    sync_date: str,
) -> str:
    """Render ``next-session`` anchor body (§GSP.5.3) — no paste fence."""
    assert decision.row is not None
    assert decision.emit_model is not None
    assert decision.step_label is not None
    row = decision.row
    model = decision.emit_model
    step_id = decision.step_label
    title = phase_tokens(row.phase_label)[0] if phase_tokens(row.phase_label) else step_id
    branch = _branch_value(config, step_id)
    read_first = _docs_read_first(config)
    position = _current_position(roadmap_text, row)
    landed = _landed_table_row(roadmap_text)

    lines = [
        f"## NEXT SESSION — {title}",
        "",
        f"**Date:** {sync_date}  ",
        f"**Current position:** {position}  ",
        f"**Model:** {model}",
        "",
        "### What just landed",
        "",
        "| Slice | Deliverable |",
        "| --- | --- |",
        landed,
        "",
        f"### THE ONE NEXT STEP — **Model: {model}**",
        "",
        row.deliverable.strip() or f"Advance {step_id}.",
        "",
        "| | |",
        "| --- | --- |",
        f"| **ID** | **{step_id}** |",
        f"| **Branch** | {branch} |",
        f"| **Repo** | **{config.repo.name}** |",
        f"| **Read first** | {read_first} |",
        f"| **Hard stops** | {HARD_STOPS} |",
    ]
    return "\n".join(lines)


def render_paste_ready(
    *,
    decision: NextRegenDecision,
    config: OverseerConfig,
) -> str:
    """Render ``paste-ready-prompt`` anchor body (§GSP.5.3 / H16)."""
    assert decision.row is not None
    assert decision.emit_model is not None
    assert decision.step_label is not None
    row = decision.row
    model = decision.emit_model
    step_id = decision.step_label
    branch = _branch_value(config, step_id).strip("`")
    read_first = _docs_read_first(config)
    title = phase_tokens(row.phase_label)[0] if phase_tokens(row.phase_label) else step_id

    fence_lines = [
        f"{step_id} — {title} ({config.repo.name}).",
        "",
        f"Model: {model}",
        f"Repo: {config.repo.name}",
        f"Branch: {branch}",
        f"Step: {step_id}",
        "Authority: authoritative",
        "",
        f"Read first: {read_first}.",
        "",
        "Deliverables:",
        f"- {row.deliverable.strip() or step_id}",
        "",
        f"Hard stops: {HARD_STOPS}",
        "",
        "Governance sync: update roadmap + handover on completion.",
    ]
    if model == "Auto" or decision.is_step_b:
        fence_lines.append("")
        fence_lines.extend(BUILD_VERIFICATION_LINES)

    fence_body = "\n".join(fence_lines)
    return "\n".join(
        [
            f"### Paste-ready prompt — {step_id}",
            "",
            "```text",
            fence_body,
            "```",
        ]
    )


def format_next_regen_token(decision: NextRegenDecision) -> str:
    """Plan/result token for dry-run and change-log (§GSP.4.3 / §GSP.6.2)."""
    if decision.row is not None and decision.reason is None:
        return "next_regen: regenerated"
    reason = decision.reason or "unknown"
    return f"next_regen: human_authorship_required ({reason})"


def format_change_log_fragment(decision: NextRegenDecision) -> str:
    """Additive change-log fragment (§GSP.6.2)."""
    if decision.row is not None and decision.reason is None:
        return "next_regen=regenerated"
    reason = decision.reason or "unknown"
    return f"next_regen=human_authorship_required:{reason}"

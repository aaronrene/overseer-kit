"""Templated section replacement for handover + roadmap (§4 / §GSP)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from adapters.config import OverseerConfig
from tools.governance_hygiene.anchors import replace_anchor_block
from tools.governance_hygiene.drift import merged_prs_missing_from_done
from tools.governance_hygiene.next_regen import (
    LAND_PHASE_A,
    LAND_PHASE_B,
    LAND_PHASE_UNREADABLE,
    NextRegenDecision,
    REASON_LAND_A_WAIT,
    REASON_LAND_PHASE_UNREADABLE,
    ensure_primary_next_marker,
    extract_paste_pr_number,
    format_change_log_fragment,
    format_next_regen_token,
    plan_land_b,
    plan_next_regen,
    render_land_b_next_session,
    render_land_b_paste,
    render_next_session,
    render_paste_ready,
    resolve_land_phase,
    set_marker_land_phase,
)
from tools.governance_hygiene.parse import normalize_status, parse_queue_rows, phase_tokens, pr_matches_row
from tools.governance_hygiene.types import QueueRow
from tools.governance_hygiene.types import DriftReport, MergedPullRequest, VerifiedReads


def build_handover_patches(
    handover_text: str,
    reads: VerifiedReads,
    drift: DriftReport,
    *,
    realign_summary: str | None,
    sync_date: str | None = None,
    config: OverseerConfig,
    roadmap_text: str,
    repo_root: Path,
) -> tuple[str, tuple[str, ...], str]:
    """Return patched handover text, touched sections, and ``next_regen`` token.

    ``roadmap_text`` must be the D3-reconciled roadmap (§GSP.6.1).
    """
    today = sync_date or date.today().isoformat()
    sections: list[str] = []
    text = handover_text

    vcs_body = _render_vcs_table(reads, today)
    text = replace_anchor_block(text, "vcs-table", vcs_body)
    sections.append("vcs-table")

    missing_prs = merged_prs_missing_from_done(text, reads.r4_merged_prs)
    if missing_prs:
        done_body = _render_done_recently(text, missing_prs)
        text = replace_anchor_block(text, "done-recently", done_body)
        sections.append("done-recently")

    snapshot_body = _render_verified_snapshot(reads, drift)
    text = replace_anchor_block(text, "verified-snapshot", snapshot_body)
    sections.append("verified-snapshot")

    # §PMHF.3.4: land-a NEXT + post-merge-incomplete signals → emit land-b for the
    # same slice; never re-emit land-a and never clobber a mid-wait land-a paste.
    main_branch = config.vcs.git.main_branch or "main"
    merged_pr_numbers = {pr.number for pr in reads.r4_merged_prs}
    paste_pr = extract_paste_pr_number(text)
    land_b = plan_land_b(
        text,
        d1=drift.d1_handover_vs_git,
        merged_pr_signal=paste_pr is not None and paste_pr in merged_pr_numbers,
        main_branch=main_branch,
    )
    current_land_phase = resolve_land_phase(text)

    if land_b is not None:
        text = ensure_primary_next_marker(text, config)
        next_body = render_land_b_next_session(land_b, config=config, sync_date=today)
        paste_body = render_land_b_paste(land_b, config=config)
        text = replace_anchor_block(text, "next-session", next_body)
        text = replace_anchor_block(text, "paste-ready-prompt", paste_body)
        text = set_marker_land_phase(text, LAND_PHASE_B)
        sections.append("next-session")
        sections.append("paste-ready-prompt")
        next_regen_token = "next_regen: regenerated (land-b)"
        next_regen_fragment = "next_regen=regenerated:land-b"
    elif current_land_phase == LAND_PHASE_A:
        # Mid-land wait: preserve the land-a NEXT/paste; fail closed on regen.
        decision = NextRegenDecision(None, REASON_LAND_A_WAIT, None, None, False)
        next_regen_token = format_next_regen_token(decision)
        next_regen_fragment = format_change_log_fragment(decision)
    elif current_land_phase == LAND_PHASE_UNREADABLE:
        decision = NextRegenDecision(None, REASON_LAND_PHASE_UNREADABLE, None, None, False)
        next_regen_token = format_next_regen_token(decision)
        next_regen_fragment = format_change_log_fragment(decision)
    else:
        decision = plan_next_regen(
            roadmap_text=roadmap_text,
            handover_text=text,
            config=config,
            repo_root=repo_root,
        )
        if decision.row is not None and decision.reason is None:
            text = ensure_primary_next_marker(text, config)
            next_body = render_next_session(
                decision=decision,
                roadmap_text=roadmap_text,
                config=config,
                sync_date=today,
            )
            paste_body = render_paste_ready(decision=decision, config=config)
            text = replace_anchor_block(text, "next-session", next_body)
            text = replace_anchor_block(text, "paste-ready-prompt", paste_body)
            # §PMHF.3.4 rule 2: a regenerated non-land NEXT clears land-phase.
            text = set_marker_land_phase(text, None)
            sections.append("next-session")
            sections.append("paste-ready-prompt")
        next_regen_token = format_next_regen_token(decision)
        next_regen_fragment = format_change_log_fragment(decision)
    change_line = _render_change_log_line(
        drift,
        reads,
        realign_summary,
        today,
        next_regen_fragment=next_regen_fragment,
    )
    text = _append_change_log(text, change_line)
    sections.append("change-log")

    return text, tuple(sections), next_regen_token


def build_roadmap_patches(
    roadmap_text: str,
    reads: VerifiedReads,
    drift: DriftReport,
) -> tuple[str, tuple[str, ...]]:
    """Return patched roadmap text and touched section names."""
    sections: list[str] = []
    text = roadmap_text

    if drift.d3_queue_vs_merged == "drifted":
        text = _patch_queue_rows(text, reads.r4_merged_prs)
        sections.append("build-queue")

    glance = _render_next_step_glance(text)
    text = replace_anchor_block(text, "next-step-glance", glance)
    sections.append("next-step-glance")

    return text, tuple(sections)


def _render_vcs_table(reads: VerifiedReads, today: str) -> str:
    dirty = "yes" if reads.r5_dirty else "no"
    lines = [
        f"## VCS (verified {today})",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| Branch | `{reads.r5_branch}` |",
    ]
    if reads.r1_github_main_sha:
        lines.append(f"| GitHub `main` | `{reads.r1_github_main_sha}` |")
    lines.append(f"| Canonical anchor | `{reads.r2_anchor_sha}` ({reads.r2_source}) |")
    if reads.r3_canonical_main_sha and reads.regime != "git-only":
        lines.append(f"| Muse `main` | `{reads.r3_canonical_main_sha}` |")
    lines.append(f"| Dirty | {dirty} |")
    return "\n".join(lines)


def _render_done_recently(handover_text: str, new_prs: list[MergedPullRequest]) -> str:
    existing_rows: list[str] = []
    capture = False
    for line in handover_text.splitlines():
        if line.strip().startswith("### What just landed"):
            capture = True
            continue
        if capture and line.startswith("### "):
            break
        if capture and line.startswith("|") and "---" not in line and "Slice" not in line:
            existing_rows.append(line)

    new_rows = [
        f"| PR #{pr.number} | {pr.title} (merged {pr.merged_at[:10] if pr.merged_at else 'unknown'}) |"
        for pr in new_prs
    ]
    rows = new_rows + existing_rows
    body = [
        "### What just landed",
        "",
        "| Slice | Deliverable |",
        "| --- | --- |",
        *rows,
    ]
    return "\n".join(body)


def _render_verified_snapshot(reads: VerifiedReads, drift: DriftReport) -> str:
    lines = [
        "## Verified snapshot",
        "",
        "| Area | State |",
        "| --- | --- |",
        f"| **VCS regime** | `{reads.r5_regime}` |",
    ]
    if reads.r1_github_main_sha:
        lines.append(f"| **GitHub main** | `{reads.r1_github_main_sha}` |")
    lines.append(f"| **Canonical anchor** | `{reads.r2_anchor_sha}` |")
    if reads.r3_canonical_main_sha:
        lines.append(f"| **Canonical main** | `{reads.r3_canonical_main_sha}` |")
    lines.append(f"| **Branch** | `{reads.r5_branch}` |")
    lines.append(f"| **Dirty** | `{'yes' if reads.r5_dirty else 'no'}` |")
    lines.append(
        f"| **Drift** | D1={drift.d1_handover_vs_git}, D2={drift.d2_anchor_vs_canonical}, "
        f"D3={drift.d3_queue_vs_merged} |"
    )
    return "\n".join(lines)


def _render_change_log_line(
    drift: DriftReport,
    reads: VerifiedReads,
    realign_summary: str | None,
    today: str,
    *,
    next_regen_fragment: str | None = None,
) -> str:
    parts = [
        f"D1={drift.d1_handover_vs_git}",
        f"D2={drift.d2_anchor_vs_canonical}",
        f"D3={drift.d3_queue_vs_merged}",
    ]
    summary = f"governance-sync: drift ({', '.join(parts)})"
    if reads.r1_github_main_sha:
        summary += f" @ `{reads.r1_github_main_sha[:7]}`"
    if realign_summary:
        summary += f"; realign: {realign_summary}"
    if next_regen_fragment:
        summary += f"; {next_regen_fragment}"
    return f"- **{today}** — {summary}"


def _append_change_log(text: str, line: str) -> str:
    if line in text:
        return text
    marker = "## Change log"
    if marker not in text:
        return text.rstrip() + f"\n\n{marker}\n\n{line}\n"
    return text.replace(marker, f"{marker}\n\n{line}", 1)


def _patch_queue_rows(roadmap_text: str, merged_prs: tuple[MergedPullRequest, ...]) -> str:
    lines = roadmap_text.splitlines()
    out: list[str] = []
    in_queue = False
    for line in lines:
        if line.strip().startswith("## Build queue"):
            in_queue = True
            out.append(line)
            continue
        if in_queue and line.startswith("## "):
            in_queue = False
        if in_queue and line.startswith("|") and "---" not in line and "Phase |" not in line:
            row = _maybe_merge_row(line, merged_prs)
            out.append(row)
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if roadmap_text.endswith("\n") else "")


def _maybe_merge_row(line: str, merged_prs: tuple[MergedPullRequest, ...]) -> str:
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    if len(cells) < 4:
        return line
    phase_label = cells[0]
    status = normalize_status(cells[2])
    if status in {"DONE", "MERGED"}:
        return line
    probe = QueueRow(
        phase_label=phase_label,
        model="",
        status="",
        deliverable="",
        raw_line=line,
    )
    for pr in merged_prs:
        if pr_matches_row(pr.title, probe):
            cells[2] = f"**DONE** (PR #{pr.number}, `{pr.merge_commit_sha[:7]}`)"
            return "| " + " | ".join(cells) + " |"
    return line


def _render_next_step_glance(roadmap_text: str) -> str:
    """Fail-closed glance: only emit a NEXT when open-row count is exactly one (§GSP.4.2)."""
    rows = parse_queue_rows(roadmap_text)
    next_rows = [row for row in rows if normalize_status(row.status) in {"TODO", "NEXT", "WIP"}]
    if len(next_rows) != 1:
        return "\n".join(
            [
                "## Next step at a glance",
                "",
                "_No unambiguous NEXT row — operator authorship required._",
            ]
        )
    row = next_rows[0]
    tokens = phase_tokens(row.phase_label)
    phase_id = tokens[0] if tokens else row.phase_label
    return "\n".join(
        [
            "## Next step at a glance",
            "",
            f"**Next:** {row.phase_label} — **Model:** {row.model} — **Status:** {row.status}",
            f"**Phase ID:** {phase_id}",
        ]
    )


def extract_paste_ready_block(handover_text: str) -> str | None:
    """Return the fenced paste-ready prompt block if present."""
    match = re.search(r"### Paste-ready prompt[\s\S]*?```[\s\S]*?```", handover_text)
    return match.group(0) if match else None

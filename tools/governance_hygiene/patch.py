"""Templated section replacement for handover + roadmap (§4)."""

from __future__ import annotations

import re
from datetime import date

from adapters.config import OverseerConfig
from tools.governance_hygiene.anchors import replace_anchor_block
from tools.governance_hygiene.drift import merged_prs_missing_from_done
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
) -> tuple[str, tuple[str, ...]]:
    """Return patched handover text and the list of touched section names."""
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

    change_line = _render_change_log_line(drift, reads, realign_summary, today)
    text = _append_change_log(text, change_line)
    sections.append("change-log")

    return text, tuple(sections)


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
    rows = parse_queue_rows(roadmap_text)
    next_rows = [row for row in rows if normalize_status(row.status) in {"TODO", "NEXT", "WIP"}]
    if not next_rows:
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

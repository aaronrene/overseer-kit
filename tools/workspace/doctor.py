"""Workspace doctor diagnostics (§MR.7.1 / §MR.6.5)."""

from __future__ import annotations

import os
from pathlib import Path

from adapters.config import OverseerConfig
from tools.workspace.check_next import resolve_member_boards
from tools.workspace.manifest import discover_manifest
from tools.workspace.next_extract import extract_next_blocks, legacy_forbidden_archived_headings
from tools.workspace.types import DoctorFinding, DoctorReport, WorkspaceLoadError


def run_doctor(
    config: OverseerConfig,
    repo_root: Path,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
    invoke_git: bool = True,
) -> DoctorReport:
    """Collect diagnostics; never merges/pushes. Regime-aware git/gh skip for muse-only."""
    if config.workspace is None:
        return DoctorReport(configured=False, findings=(), ok=True)

    findings: list[DoctorFinding] = []
    try:
        manifest = discover_manifest(config, repo_root, environ=environ, home=home)
    except WorkspaceLoadError as exc:
        return DoctorReport(
            configured=True,
            findings=(DoctorFinding(code="error", message=str(exc)),),
            ok=False,
        )
    assert manifest is not None

    if manifest.manifest_source == "home_index":
        findings.append(
            DoctorFinding(
                code="manifest_source_home_index",
                message="manifest loaded from ~/.overseer/workspaces (last resort)",
                path=str(manifest.source_path),
            )
        )

    boards = resolve_member_boards(manifest, environ=environ, home=home)
    for board in boards:
        if board.member_status == "absent":
            findings.append(
                DoctorFinding(
                    code="member_absent",
                    message=f"optional member {board.member_id} absent",
                    member_id=board.member_id,
                )
            )
            continue
        if board.member_status == "missing_required":
            findings.append(
                DoctorFinding(
                    code="missing_member",
                    message=f"required member {board.member_id} missing",
                    member_id=board.member_id,
                )
            )
            continue
        if board.board_name_violation:
            findings.append(
                DoctorFinding(
                    code="board_name_violation",
                    message=(
                        f"board_name_violation: {board.member_id} "
                        f"handover={board.handover_basename!r} "
                        f"roadmap={board.roadmap_basename!r} "
                        f"(expected {{REPO_SLUG}}-OVERSEER-HANDOVER.md / {{REPO_SLUG}}-ROADMAP.md)"
                    ),
                    member_id=board.member_id,
                    path=str(board.handover_path) if board.handover_path else None,
                )
            )

        if board.root is None:
            continue

        # Regime mismatch advisory
        member_row = manifest.member(board.member_id)
        if member_row and member_row.regime and board.regime and member_row.regime != board.regime:
            findings.append(
                DoctorFinding(
                    code="regime_mismatch",
                    message=(
                        f"regime_mismatch: manifest {member_row.regime!r} != "
                        f"member config {board.regime!r}"
                    ),
                    member_id=board.member_id,
                )
            )

        # muse-only: never invoke git/gh (S5)
        regime = board.regime or (member_row.regime if member_row else None)
        if regime == "muse-only":
            # Explicitly skip git — record that we honored the guard when asked.
            if invoke_git:
                findings.append(
                    DoctorFinding(
                        code="muse_only_skip_git",
                        message=f"skipped git/gh for muse-only member {board.member_id}",
                        member_id=board.member_id,
                    )
                )
        elif invoke_git and regime == "muse+git-mirror" and board.root is not None:
            # Advisory muse≠git only when .muse and .git both present — no network.
            muse_head = board.root / ".muse" / "HEAD"
            git_dir = board.root / ".git"
            if muse_head.is_file() and git_dir.exists():
                try:
                    muse_sha = muse_head.read_text(encoding="utf-8").strip().split()[-1]
                except OSError:
                    muse_sha = ""
                git_head = board.root / ".git" / "HEAD"
                # Soft note only — do not shell git for muse-only; for muse+git we may read files.
                if muse_sha and git_head.is_file():
                    findings.append(
                        DoctorFinding(
                            code="muse_sync_advisory",
                            message=f"muse HEAD present for {board.member_id}; use ok status for muse_sync gate",
                            member_id=board.member_id,
                        )
                    )

        if board.handover_path and board.handover_path.is_file():
            text = board.handover_path.read_text(encoding="utf-8")
            if legacy_forbidden_archived_headings(text):
                findings.append(
                    DoctorFinding(
                        code="forbidden_archived_next",
                        message=f"forbidden ## NEXT SESSION — … archived … in {board.handover_path}",
                        member_id=board.member_id,
                        path=str(board.handover_path),
                    )
                )
            blocks = extract_next_blocks(text)
            if any(b.unmarked for b in blocks):
                findings.append(
                    DoctorFinding(
                        code="unmarked_next",
                        message=f"unmarked ## NEXT SESSION — on {board.handover_path}",
                        member_id=board.member_id,
                        path=str(board.handover_path),
                    )
                )

    hard = {
        "error",
        "missing_member",
        "board_name_violation",
        "forbidden_archived_next",
    }
    # Doctor ok is advisory: board_name_violation is reported but does not make
    # doctor exit non-zero by itself for CLI (freeze: doctor surfaces UX debt).
    # We still set ok=False when required members missing or config error.
    ok = not any(f.code in {"error", "missing_member"} for f in findings)
    return DoctorReport(configured=True, findings=tuple(findings), ok=ok)

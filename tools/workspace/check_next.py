"""Relay freshness predicate and member board resolution (§MR.5 / §MR.7)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from adapters.config import OverseerConfig
from cli.docs_paths import living_doc_abs
from tools.workspace.board_names import board_name_violation
from tools.workspace.manifest import (
    discover_manifest,
    load_member_config,
    resolve_member_root,
)
from tools.workspace.next_extract import (
    count_next_session_headings,
    extract_next_blocks,
    heading_role_mismatch,
    legacy_forbidden_archived_headings,
    primary_paste_hash,
    select_live_primary,
    select_product_tip,
    with_computed_hash,
)
from tools.workspace.types import (
    EXIT_CONFIG,
    EXIT_OK,
    EXIT_WORKSPACE_RELAY,
    CheckNextResult,
    FreshnessFinding,
    MemberBoardPaths,
    NextRole,
    RelayState,
    WorkspaceLoadError,
    WorkspaceManifest,
    WorkspaceStatusReport,
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_member_boards(
    manifest: WorkspaceManifest,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
    strict_all: bool = False,
) -> list[MemberBoardPaths]:
    """Resolve each member's root and default-lane board paths."""
    env = environ if environ is not None else dict(os.environ)
    out: list[MemberBoardPaths] = []
    for member in manifest.members:
        root = resolve_member_root(member.root_raw, environ=env, home=home)
        if root is None or not root.is_dir() or not (root / ".overseer" / "config.yaml").is_file():
            status = "missing_required" if member.required else "absent"
            if member.required or strict_all:
                # required missing always missing_required
                status = "missing_required" if member.required else "absent"
            out.append(
                MemberBoardPaths(
                    member_id=member.id,
                    root=root,
                    present=False,
                    handover_path=None,
                    roadmap_path=None,
                    handover_basename=None,
                    roadmap_basename=None,
                    handover_title=None,
                    roadmap_title=None,
                    regime=member.regime,
                    role=member.role,
                    relay=member.relay,
                    required=member.required,
                    member_status=status,  # type: ignore[arg-type]
                )
            )
            continue
        try:
            cfg = load_member_config(root)
        except WorkspaceLoadError as exc:
            out.append(
                MemberBoardPaths(
                    member_id=member.id,
                    root=root,
                    present=True,
                    handover_path=None,
                    roadmap_path=None,
                    handover_basename=None,
                    roadmap_basename=None,
                    handover_title=None,
                    roadmap_title=None,
                    regime=member.regime,
                    role=member.role,
                    relay=member.relay,
                    required=member.required,
                    member_status="error",
                    error=str(exc),
                )
            )
            continue

        handover_name = member.handover or cfg.docs.handover
        roadmap_name = member.roadmap or cfg.docs.roadmap
        handover_path = living_doc_abs(root, cfg, handover_name)
        roadmap_path = living_doc_abs(root, cfg, roadmap_name)
        # Prefer join via docs root for basename (config may store bare filename)
        handover_basename = Path(handover_name).name
        roadmap_basename = Path(roadmap_name).name
        violation = board_name_violation(
            repo_name=cfg.repo.name,
            handover_basename=handover_basename,
            roadmap_basename=roadmap_basename,
            strict=manifest.strict_board_names,
        )
        out.append(
            MemberBoardPaths(
                member_id=member.id,
                root=root,
                present=True,
                handover_path=handover_path if handover_path.is_file() else None,
                roadmap_path=roadmap_path if roadmap_path.is_file() else None,
                handover_basename=handover_basename,
                roadmap_basename=roadmap_basename,
                handover_title=cfg.docs.handover_title,
                roadmap_title=cfg.docs.roadmap_title,
                regime=cfg.vcs.regime,
                role=member.role,
                relay=member.relay,
                required=member.required,
                member_status="ok",
                board_name_violation=violation,
            )
        )
    return out


def _primary_snapshot(path: Path, text: str, *, lane: str, strict_markers: bool) -> tuple[dict[str, Any] | None, list[FreshnessFinding]]:
    findings: list[FreshnessFinding] = []
    forbidden = legacy_forbidden_archived_headings(text)
    if forbidden:
        findings.append(
            FreshnessFinding(
                code="ambiguous_primary",
                message=(
                    f"forbidden legacy archived NEXT heading at {path}:{forbidden[0][0]}: "
                    f"{forbidden[0][1]}"
                ),
                primary_path=str(path),
            )
        )

    blocks = extract_next_blocks(text)
    next_count = count_next_session_headings(text)
    if next_count != 1:
        findings.append(
            FreshnessFinding(
                code="ambiguous_primary",
                message=f"expected exactly one ## NEXT SESSION — heading, found {next_count}",
                primary_path=str(path),
            )
        )

    unmarked = [b for b in blocks if b.unmarked]
    if unmarked:
        if strict_markers:
            findings.append(
                FreshnessFinding(
                    code="ambiguous_primary",
                    message=f"unmarked_next at {path}:{unmarked[0].heading_line}",
                    primary_path=str(path),
                )
            )
        else:
            findings.append(
                FreshnessFinding(
                    code="ok",
                    message=f"unmarked_next warning at {path}:{unmarked[0].heading_line}",
                    primary_path=str(path),
                )
            )

    primaries = [
        b
        for b in blocks
        if b.role is NextRole.PRIMARY and b.status == "live" and not b.unmarked and (b.lane is None or b.lane == lane)
    ]
    if len(primaries) > 1:
        findings.append(
            FreshnessFinding(
                code="ambiguous_primary",
                message=f"multiple LIVE PRIMARY markers on {path}",
                primary_path=str(path),
            )
        )
        return None, findings
    if len(primaries) == 0:
        # Try unmarked only when not strict
        if not strict_markers and unmarked:
            block = with_computed_hash(unmarked[0])
        else:
            findings.append(
                FreshnessFinding(
                    code="missing_primary",
                    message=f"missing_primary on {path}",
                    primary_path=str(path),
                )
            )
            return None, findings
    else:
        block = with_computed_hash(primaries[0])
        mismatch = heading_role_mismatch(block)
        if mismatch:
            findings.append(
                FreshnessFinding(
                    code="ambiguous_primary",
                    message=f"{mismatch} at {path}:{block.heading_line}",
                    primary_path=str(path),
                )
            )

    digest = primary_paste_hash(block)
    if not digest or not block.step_id or not block.model:
        findings.append(
            FreshnessFinding(
                code="missing_primary",
                message=f"PRIMARY fence missing Step/Model/fence on {path}",
                primary_path=str(path),
            )
        )
        return None, findings

    snap = {
        "path": str(path),
        "step_id": block.step_id,
        "model": block.model,
        "tip_hash": digest,
        "lane": lane,
        "heading": block.heading,
    }
    # Drop soft "ok" warnings from hard-fail codes
    hard = [f for f in findings if f.code != "ok"]
    if hard:
        return snap, findings
    return snap, findings


def check_next(
    manifest: WorkspaceManifest,
    *,
    lane: str | None = None,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
    strict_all: bool = False,
) -> CheckNextResult:
    """Evaluate relay freshness for the product lane (or ``--lane``)."""
    target_lane = lane or manifest.primary_lane().id
    boards = resolve_member_boards(manifest, environ=environ, home=home, strict_all=strict_all)
    by_id = {b.member_id: b for b in boards}
    findings: list[FreshnessFinding] = []

    for board in boards:
        if board.member_status == "missing_required":
            findings.append(
                FreshnessFinding(
                    code="missing_member",
                    message=f"required member {board.member_id!r} missing or incomplete",
                )
            )
    if any(f.code == "missing_member" for f in findings):
        return CheckNextResult(
            exit_code=EXIT_WORKSPACE_RELAY,
            state="missing_member",
            ok=False,
            lane=target_lane,
            findings=tuple(findings),
            messages=tuple(f.message for f in findings),
        )

    po_member = manifest.product_order()
    po_board = by_id.get(po_member.id)
    if po_board is None or po_board.handover_path is None:
        findings.append(
            FreshnessFinding(
                code="missing_primary",
                message=f"product_order handover missing for {po_member.id}",
            )
        )
        return CheckNextResult(
            exit_code=EXIT_WORKSPACE_RELAY,
            state="missing_primary",
            ok=False,
            lane=target_lane,
            findings=tuple(findings),
            messages=tuple(f.message for f in findings),
        )

    po_text = _read_text(po_board.handover_path)
    primary, po_findings = _primary_snapshot(
        po_board.handover_path,
        po_text,
        lane=target_lane,
        strict_markers=manifest.strict_markers,
    )
    findings.extend([f for f in po_findings if f.code != "ok"])
    soft_warnings = [f.message for f in po_findings if f.code == "ok"]

    hard_codes = {f.code for f in findings}
    if "ambiguous_primary" in hard_codes:
        return CheckNextResult(
            exit_code=EXIT_WORKSPACE_RELAY,
            state="ambiguous_primary",
            ok=False,
            lane=target_lane,
            findings=tuple(findings),
            primary=primary,
            messages=tuple(f.message for f in findings),
        )
    if primary is None or "missing_primary" in hard_codes:
        return CheckNextResult(
            exit_code=EXIT_WORKSPACE_RELAY,
            state="missing_primary",
            ok=False,
            lane=target_lane,
            findings=tuple(findings),
            primary=primary,
            messages=tuple(f.message for f in findings),
        )

    relay_rows: list[dict[str, Any]] = []
    for member in manifest.members:
        if not member.relay:
            continue
        board = by_id[member.id]
        if board.member_status == "absent":
            continue
        if board.handover_path is None:
            findings.append(
                FreshnessFinding(
                    code="stale_relay",
                    message=f"stale_relay: {member.id} handover missing",
                    relay_path=None,
                    primary_path=primary["path"],
                )
            )
            continue
        text = _read_text(board.handover_path)
        if legacy_forbidden_archived_headings(text):
            findings.append(
                FreshnessFinding(
                    code="ambiguous_primary",
                    message=f"forbidden legacy archived NEXT on relay {board.handover_path}",
                    relay_path=str(board.handover_path),
                    primary_path=primary["path"],
                )
            )
            continue
        blocks = extract_next_blocks(text)
        unmarked = [b for b in blocks if b.unmarked]
        if unmarked and manifest.strict_markers:
            findings.append(
                FreshnessFinding(
                    code="ambiguous_primary",
                    message=f"unmarked_next on relay {board.handover_path}:{unmarked[0].heading_line}",
                    relay_path=str(board.handover_path),
                    primary_path=primary["path"],
                )
            )
            continue

        tip, tip_err = select_product_tip(blocks, lane=target_lane)
        if tip_err == "ambiguous_primary":
            findings.append(
                FreshnessFinding(
                    code="ambiguous_primary",
                    message=(
                        f"ambiguous_primary: both role=relay and role=product_relay "
                        f"on {board.handover_path}"
                    ),
                    relay_path=str(board.handover_path),
                    primary_path=primary["path"],
                )
            )
            continue
        if tip is None:
            findings.append(
                FreshnessFinding(
                    code="stale_relay",
                    message=(
                        f"stale_relay: {board.handover_path} missing product tip "
                        f"(relay or product_relay)"
                    ),
                    relay_path=str(board.handover_path),
                    primary_path=primary["path"],
                )
            )
            continue

        tip_hash = (tip.tip_hash or "").lower()
        tip_step = tip.step_id
        tip_model = tip.model
        # When tip_hash missing on marker, try fence hash only for embed mode
        if not tip_hash and tip.fence:
            from tools.workspace.next_extract import tip_hash_hex

            tip_hash = tip_hash_hex(tip.fence)

        row = {
            "member_id": member.id,
            "path": str(board.handover_path),
            "role": tip.role.value,
            "step_id": tip_step,
            "model": tip_model,
            "tip_hash": tip_hash,
            "product_order": tip.product_order,
        }
        relay_rows.append(row)

        mismatches: list[str] = []
        if tip_step != primary["step_id"]:
            mismatches.append(f"step_id {tip_step!r}!={primary['step_id']!r}")
        if tip_model != primary["model"]:
            mismatches.append(f"model {tip_model!r}!={primary['model']!r}")
        if tip_hash != primary["tip_hash"]:
            mismatches.append(f"tip_hash sha256:{tip_hash}!=sha256:{primary['tip_hash']}")
        if tip.product_order and tip.product_order != manifest.product_order_member:
            mismatches.append(
                f"product_order {tip.product_order!r}!={manifest.product_order_member!r}"
            )
        if mismatches:
            findings.append(
                FreshnessFinding(
                    code="stale_relay",
                    message=(
                        f"stale_relay: {board.handover_path} tip=({', '.join(mismatches)}) "
                        f"!= product_order {primary['path']} "
                        f"primary=(step={primary['step_id']}, model={primary['model']}, "
                        f"tip_hash=sha256:{primary['tip_hash']})"
                    ),
                    relay_path=str(board.handover_path),
                    primary_path=primary["path"],
                )
            )

    if any(f.code == "ambiguous_primary" for f in findings):
        state: RelayState = "ambiguous_primary"
        code = EXIT_WORKSPACE_RELAY
        ok = False
    elif any(f.code == "stale_relay" for f in findings):
        state = "stale_relay"
        code = EXIT_WORKSPACE_RELAY
        ok = False
    elif any(f.code == "missing_primary" for f in findings):
        state = "missing_primary"
        code = EXIT_WORKSPACE_RELAY
        ok = False
    else:
        state = "ok"
        code = EXIT_OK
        ok = True

    messages = tuple(f.message for f in findings) + tuple(soft_warnings)
    return CheckNextResult(
        exit_code=code,
        state=state,
        ok=ok,
        lane=target_lane,
        findings=tuple(findings),
        primary=primary,
        relays=tuple(relay_rows),
        messages=messages,
    )


def build_status_report(
    config: OverseerConfig,
    repo_root: Path,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
    strict_all: bool = False,
) -> WorkspaceStatusReport:
    """Build ``ok workspace status`` report (exit 0 + not_configured when absent)."""
    if config.workspace is None:
        return WorkspaceStatusReport(
            configured=False,
            ok=True,
            state="not_configured",
            constellation_id=None,
            product_order_member=None,
            manifest_source=None,
            manifest_path=None,
            authoritative_handover=None,
            members=(),
            lanes=(),
            check_next=None,
            warnings=("workspace: not_configured",),
        )

    try:
        manifest = discover_manifest(config, repo_root, environ=environ, home=home)
    except WorkspaceLoadError as exc:
        return WorkspaceStatusReport(
            configured=True,
            ok=False,
            state="error",
            constellation_id=config.workspace.constellation_id,
            product_order_member=None,
            manifest_source=None,
            manifest_path=None,
            authoritative_handover=None,
            members=(),
            lanes=(),
            check_next=None,
            warnings=(str(exc),),
            diagnostics=(str(exc),),
        )
    assert manifest is not None

    boards = resolve_member_boards(manifest, environ=environ, home=home, strict_all=strict_all)
    check = check_next(manifest, environ=environ, home=home, strict_all=strict_all)

    member_payloads: list[dict[str, Any]] = []
    for board in boards:
        member_payloads.append(
            {
                "id": board.member_id,
                "role": board.role,
                "relay": board.relay,
                "required": board.required,
                "regime": board.regime,
                "root": str(board.root) if board.root else None,
                "member_status": board.member_status,
                "handover_basename": board.handover_basename,
                "roadmap_basename": board.roadmap_basename,
                "handover_title": board.handover_title,
                "roadmap_title": board.roadmap_title,
                "handover_path": str(board.handover_path) if board.handover_path else None,
                "board_name_violation": board.board_name_violation,
                "error": board.error,
            }
        )

    lane_payloads = [
        {
            "id": lane.id,
            "primary": lane.primary,
            "owner_member": lane.owner_member or manifest.product_order_member,
        }
        for lane in manifest.lanes
    ]

    po_board = next((b for b in boards if b.member_id == manifest.product_order_member), None)
    authoritative = None
    if po_board and po_board.handover_path:
        authoritative = str(po_board.handover_path)
    elif po_board and po_board.handover_basename and po_board.root:
        authoritative = str(po_board.root / "docs" / po_board.handover_basename)

    warnings: list[str] = []
    if manifest.manifest_source == "home_index":
        warnings.append("manifest_source: home_index (last resort — prefer product_order)")

    return WorkspaceStatusReport(
        configured=True,
        ok=check.ok,
        state=check.state,
        constellation_id=manifest.id,
        product_order_member=manifest.product_order_member,
        manifest_source=manifest.manifest_source,
        manifest_path=str(manifest.source_path),
        authoritative_handover=authoritative,
        members=tuple(member_payloads),
        lanes=tuple(lane_payloads),
        check_next={
            "ok": check.ok,
            "state": check.state,
            "exit_code": check.exit_code,
            "lane": check.lane,
            "primary": check.primary,
            "relays": list(check.relays),
            "messages": list(check.messages),
        },
        warnings=tuple(warnings),
    )


def workspace_relay_footer_state(
    config: OverseerConfig,
    repo_root: Path,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
) -> RelayState:
    """Read-only workspace_relay state for governance-sync footer (§MR.8)."""
    if config.workspace is None:
        return "not_configured"
    try:
        manifest = discover_manifest(config, repo_root, environ=environ, home=home)
        if manifest is None:
            return "not_configured"
        result = check_next(manifest, environ=environ, home=home)
        return result.state
    except WorkspaceLoadError:
        return "error"


def load_manifest_for_repo(
    config: OverseerConfig,
    repo_root: Path,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
) -> WorkspaceManifest:
    """Load manifest or raise WorkspaceLoadError / signal not configured."""
    if config.workspace is None:
        raise WorkspaceLoadError("workspace not configured", citation=str(repo_root))
    manifest = discover_manifest(config, repo_root, environ=environ, home=home)
    if manifest is None:
        raise WorkspaceLoadError("workspace not configured", citation=str(repo_root))
    return manifest

"""``overseer status`` command (§K4.4)."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from adapters.config import load_config
from adapters.errors import ConfigError, ReadError
from cli.context import CliContext
from cli.digest import FootprintRecord, compute_footprint_digest, sha256_hex
from cli.drift import compute_drift
from cli.footprint import resolve_footprint
from cli.kit_root import kit_version
from cli.output import CommandReport
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error, sanitize_text
from cli.vcs_status import read_vcs_status, vcs_report
from cli.version_lock import LockError, lock_path, read_version_lock


GOVERNANCE_SYNC_MARKER = "last_governance_sync"


def _read_governance_sync_marker(repo_root: Path) -> str | None:
    marker = repo_root / ".overseer" / GOVERNANCE_SYNC_MARKER
    if not marker.is_file():
        return None
    text = marker.read_text(encoding="utf-8").strip()
    return text or None


def _compute_footprint_integrity(
    repo_root: Path,
    lock,
    rendered,
) -> str:
    """Recompute digest from on-disk footprint bytes and compare to lock."""
    records: list[FootprintRecord] = []
    for item in rendered:
        dest = repo_root / item.destination
        if dest.is_file():
            content = dest.read_bytes()
        else:
            content = b""
        records.append(FootprintRecord(path=item.destination, sha256_hex=sha256_hex(content)))
    records.sort(key=lambda row: row.path)
    computed = compute_footprint_digest(records)
    return "ok" if computed == lock.footprint_digest else "mismatch"


def _lock_summary(lock) -> dict:
    return {
        "lock_version": lock.lock_version,
        "kit_version": lock.kit_version,
        "config_version": lock.config_version,
        "footprint_digest": lock.footprint_digest,
        "installed_at": lock.installed_at,
        "synced_at": lock.synced_at,
    }


def _exit_code_from_conditions(
    *,
    config_error: bool,
    integrity: str | None,
    drift_status: str | None,
    use_exit_code: bool,
) -> int:
    """Apply frozen precedence: 2 > 6 > 3 > 0."""
    if not use_exit_code:
        return 0
    if config_error:
        return 2
    if integrity == "mismatch":
        return 6
    if drift_status in {"behind", "ahead"}:
        return 3
    return 0


def run_status(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer status``."""
    report = CommandReport()
    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="status")
    overseer_dir = repo_root / ".overseer"

    if not overseer_dir.is_dir():
        payload = {
            "initialized": False,
            "warnings": [],
        }
        if ctx.output.json_mode:
            ctx.output.emit_json(payload)
        else:
            ctx.output.emit("not initialized")
        return 0

    config_path = resolve_config_path(repo_root, args.config)
    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    config_error = False
    lock_error = False

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        config_error = True
        ctx.output.error(format_config_error(exc, repo_root))
        payload = {
            "initialized": True,
            "error": str(exc),
            "warnings": report.warnings,
        }
        if ctx.output.json_mode:
            ctx.output.emit_json(payload)
        return 2

    lock_file = lock_path(repo_root)
    lock = None
    try:
        lock = read_version_lock(lock_file)
    except LockError as exc:
        lock_error = True
        report.add_warning(str(exc))

    rendered: list = []
    integrity: str | None = None
    if lock is not None:
        try:
            rendered = resolve_footprint(config, kit=ctx.kit)
        except ConfigError as exc:
            config_error = True
            ctx.output.error(format_config_error(exc, repo_root))
            return 2

        if args.check_footprint:
            integrity = _compute_footprint_integrity(repo_root, lock, rendered)
            if integrity == "mismatch":
                report.add_warning("footprint_integrity: mismatch")

    drift = compute_drift(
        cli_version=kit_version(),
        lock=lock,
        rendered=rendered,
        repo_root=repo_root,
    )
    if drift["status"] in {"behind", "ahead"}:
        report.add_warning(f"drift: {drift['status']}")

    vcs_result = read_vcs_status(config, repo_root, ctx.runner)
    if isinstance(vcs_result, ReadError):
        ctx.output.error(sanitize_text(str(vcs_result), repo_root))
        payload = {
            "initialized": True,
            "vcs": {
                "error": sanitize_text(str(vcs_result), repo_root),
                "command": sanitize_text(vcs_result.command, repo_root),
            },
            "warnings": report.warnings,
        }
        if ctx.output.json_mode:
            ctx.output.emit_json(payload)
        return 2

    payload = {
        "initialized": True,
        "kit_version": kit_version(),
        "lock": _lock_summary(lock) if lock else None,
        "drift": drift,
        "footprint_integrity": integrity,
        "vcs": vcs_report(vcs_result, config),
        "last_governance_sync": _read_governance_sync_marker(repo_root),
        "warnings": report.warnings,
    }
    if lock_error:
        payload["lock_error"] = True

    exit_code = _exit_code_from_conditions(
        config_error=config_error,
        integrity=integrity if args.check_footprint else None,
        drift_status=drift["status"],
        use_exit_code=args.exit_code,
    )
    if lock_error and args.exit_code:
        exit_code = 6 if exit_code == 0 else max(exit_code, 6)

    if ctx.output.json_mode:
        ctx.output.emit_json(payload)
    else:
        ctx.output.emit(f"kit_version: {payload['kit_version']}")
        if lock:
            ctx.output.emit(f"lock kit_version: {lock.kit_version}")
        ctx.output.emit(f"drift: {drift['status']}")
        if integrity:
            ctx.output.emit(f"footprint_integrity: {integrity}")
        ctx.output.emit(f"vcs.regime: {vcs_result.regime}")
        ctx.output.emit(f"vcs.branch: {vcs_result.branch}")
        ctx.output.emit(f"vcs.dirty: {vcs_result.dirty}")

    return exit_code

"""Ledger verify, append, and show (§K9.7 / §K9.9)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from adapters.config import OverseerConfig
from cli.paths import confine_path, repo_relative
from tools.honesty.canonical import compute_entry_hash
from tools.honesty.gate import check_roles_file, honesty_module_disabled
from tools.honesty.genesis import GENESIS_PREV, build_genesis_entry, utc_now_z
from tools.honesty.ledger_io import (
    LedgerIOError,
    atomic_append_lines,
    read_ledger_entries,
    serialize_entry,
)
from tools.honesty.types import LedgerAppendOptions, LedgerResult
from tools.honesty.validate import EntryValidationError, find_passing_verdict, validate_append_body


def verify_chain(entries: list[dict[str, Any]]) -> int:
    """Walk the hash chain; return ``0`` or ``22``."""
    if not entries:
        return 0

    expected_prev = GENESIS_PREV
    for entry in entries:
        if entry.get("v") != 1:
            return 22
        stored_hash = entry.get("entry_hash")
        if not isinstance(stored_hash, str):
            return 22
        if entry.get("prev_hash") != expected_prev:
            return 22
        computed = compute_entry_hash(entry)
        if computed != stored_hash.lower():
            return 22
        expected_prev = stored_hash.lower()
    return 0


def _resolve_ledger_path(config: OverseerConfig, repo_root: Path) -> Path:
    ledger = config.honesty.ledger
    if ledger is None or not ledger.strip():
        raise ValueError("honesty.ledger missing")
    return confine_path(repo_root, ledger)


def _finalize_entry(body: dict[str, Any], prev_hash: str) -> dict[str, Any]:
    """Fill envelope hashes and default timestamp."""
    entry = dict(body)
    if not entry.get("ts"):
        entry["ts"] = utc_now_z()
    entry["prev_hash"] = prev_hash
    entry["entry_hash"] = compute_entry_hash(entry)
    return entry


def append_entry(
    *,
    config: OverseerConfig,
    repo_root: Path,
    options: LedgerAppendOptions,
) -> LedgerResult:
    """Append one or more ledger lines per §K9.9."""
    if honesty_module_disabled(config):
        return LedgerResult(exit_code=4, stderr_extra="refused: honesty.enabled is false")

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        return LedgerResult(exit_code=roles_exit)

    try:
        ledger_path = _resolve_ledger_path(config, repo_root)
    except Exception:
        return LedgerResult(exit_code=4)

    try:
        body = validate_append_body(kind=options.kind, body=dict(options.body))
    except EntryValidationError as exc:
        return LedgerResult(exit_code=exc.exit_code, stderr_extra=str(exc))

    existing = read_ledger_entries(ledger_path)

    if options.kind == "genesis" and existing:
        return LedgerResult(exit_code=2, stderr_extra="genesis on non-empty ledger")

    if options.kind == "approval_recorded":
        artifact_sha = body["artifact_sha256"]
        bound_hash = body["bound_verdict_hash"]
        if not find_passing_verdict(existing, artifact_sha256=artifact_sha, bound_verdict_hash=bound_hash):
            return LedgerResult(exit_code=21, stderr_extra="approval without bound passing verdict")

    lines_to_write: list[str] = []
    prev_hash = existing[-1]["entry_hash"].lower() if existing else GENESIS_PREV

    if not existing and options.kind != "genesis":
        genesis = build_genesis_entry()
        lines_to_write.append(serialize_entry(genesis))
        prev_hash = genesis["entry_hash"].lower()

    entry = _finalize_entry(body, prev_hash)
    lines_to_write.append(serialize_entry(entry))

    try:
        atomic_append_lines(ledger_path, lines_to_write)
    except LedgerIOError as exc:
        return LedgerResult(exit_code=5, stderr_extra=str(exc))

    stderr = roles_warn or ""
    return LedgerResult(exit_code=0, stderr_extra=stderr)


def verify_ledger_file(
    *,
    config: OverseerConfig,
    repo_root: Path,
) -> LedgerResult:
    """Verify the configured ledger chain."""
    if honesty_module_disabled(config):
        return LedgerResult(exit_code=4, stderr_extra="refused: honesty.enabled is false")

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        return LedgerResult(exit_code=roles_exit)

    try:
        ledger_path = _resolve_ledger_path(config, repo_root)
    except Exception:
        return LedgerResult(exit_code=4)

    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        return LedgerResult(exit_code=0, stderr_extra=roles_warn or "")

    try:
        entries = read_ledger_entries(ledger_path)
    except ValueError as exc:
        return LedgerResult(exit_code=22, stderr_extra=str(exc))

    code = verify_chain(entries)
    return LedgerResult(exit_code=code, stderr_extra=roles_warn or "")


def show_entries(
    *,
    config: OverseerConfig,
    repo_root: Path,
    last_n: int,
) -> LedgerResult:
    """Print the last ``N`` ledger records as JSONL."""
    if last_n < 1:
        return LedgerResult(exit_code=1, stderr_extra="usage: --last must be >= 1")

    if honesty_module_disabled(config):
        return LedgerResult(exit_code=4, stderr_extra="refused: honesty.enabled is false")

    roles_exit, roles_warn = check_roles_file(config.honesty, repo_root)
    if roles_exit is not None:
        return LedgerResult(exit_code=roles_exit)

    try:
        ledger_path = _resolve_ledger_path(config, repo_root)
    except Exception:
        return LedgerResult(exit_code=4)

    if not ledger_path.is_file() or ledger_path.stat().st_size == 0:
        return LedgerResult(exit_code=0, stderr_extra=roles_warn or "")

    try:
        entries = read_ledger_entries(ledger_path)
    except ValueError as exc:
        return LedgerResult(exit_code=22, stderr_extra=str(exc))

    window = entries[-last_n:]
    lines = [json.dumps(entry, ensure_ascii=False, separators=(",", ":"), sort_keys=True) for entry in window]
    return LedgerResult(exit_code=0, stdout_lines=lines, stderr_extra=roles_warn or "")


def parse_append_body(
    *,
    repo_root: Path,
    file_path: str | None,
    stdin_text: str | None,
) -> tuple[dict[str, Any] | None, int, str]:
    """Load append JSON body from file or stdin; return (body, exit, error)."""
    if file_path is not None:
        try:
            resolved = confine_path(repo_root, file_path)
        except Exception:
            return None, 4, "path escape"
        if not resolved.is_file():
            return None, 4, "file missing"
        try:
            text = resolved.read_text(encoding="utf-8")
            body = json.loads(text)
        except json.JSONDecodeError:
            return None, 2, "malformed JSON"
        except OSError:
            return None, 4, "unreadable"
        if not isinstance(body, dict):
            return None, 2, "body must be object"
        return body, 0, ""

    if stdin_text is not None:
        try:
            body = json.loads(stdin_text)
        except json.JSONDecodeError:
            return None, 2, "malformed JSON"
        if not isinstance(body, dict):
            return None, 2, "body must be object"
        return body, 0, ""

    return {}, 0, ""


def ledger_rel_path(config: OverseerConfig, repo_root: Path) -> str:
    """Return repo-relative ledger path for JSON payloads."""
    ledger_path = _resolve_ledger_path(config, repo_root)
    return repo_relative(repo_root, ledger_path)

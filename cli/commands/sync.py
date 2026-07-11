"""``overseer sync`` command (§K4.3 + §K6.4 preserved / ``--include-preserved``)."""

from __future__ import annotations

import difflib
import sys
from argparse import Namespace
from pathlib import Path

from adapters.config import load_config
from adapters.errors import ConfigError
from cli.atomic import WriteFailure, atomic_write_bytes
from cli.context import CliContext
from cli.digest import sha256_hex
from cli.docs_paths import living_doc_destinations, validate_muse_working_dir
from cli.footprint import resolve_footprint
from cli.kit_root import kit_version
from cli.output import CommandReport
from cli.sanitize import format_config_error, sanitize_text
from cli.paths import is_within_repo, resolve_config_path, resolve_repo_root
from cli.sync_classify import Classification, classify_footprint, matches_glob
from cli.version_lock import (
    ORIGIN_KIT,
    ORIGIN_PRESERVED,
    FootprintEntry,
    build_version_lock_from_entries,
    entry_origin,
    lock_path,
    read_version_lock,
    write_version_lock,
)


def _emit_diff(
    ctx: CliContext,
    destination: str,
    old_bytes: bytes,
    new_bytes: bytes,
) -> None:
    old_lines = old_bytes.decode("utf-8").splitlines(keepends=True)
    new_lines = new_bytes.decode("utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{destination}",
        tofile=f"b/{destination}",
    )
    for line in diff:
        ctx.output.emit(line.rstrip("\n"))


def _is_preserved_path(lock, destination: str, living: frozenset[str]) -> bool:
    """True when lock entry is ``origin: preserved`` (or living without kit origin)."""
    for entry in lock.footprint:
        if entry.path == destination:
            return entry_origin(entry) == ORIGIN_PRESERVED
    return destination in living


def _build_post_sync_entries(
    *,
    lock,
    rendered,
    only_globs: list[str],
    writes: dict[str, bytes],
    promoted: set[str],
    retain_preserved: bool,
) -> list[FootprintEntry]:
    """Build full manifest entries after sync, retaining preserved/out-of-scope verbatim."""
    prior = {entry.path: entry for entry in lock.footprint}
    entries: list[FootprintEntry] = []

    for item in sorted(rendered, key=lambda row: row.destination):
        dest = item.destination
        in_scope = not only_globs or matches_glob(dest, only_globs)
        prior_entry = prior.get(dest)

        if retain_preserved and prior_entry is not None and entry_origin(prior_entry) == ORIGIN_PRESERVED:
            if dest not in promoted:
                entries.append(prior_entry)
                continue

        if not in_scope and prior_entry is not None and dest not in promoted:
            entries.append(prior_entry)
            continue

        if dest in writes:
            content = writes[dest]
        elif prior_entry is not None and dest in promoted:
            # Ownership promotion with identical bytes — keep on-disk / rendered match
            content = item.content
        else:
            content = item.content

        origin = ORIGIN_KIT
        if prior_entry is not None and dest not in promoted and entry_origin(prior_entry) == ORIGIN_PRESERVED:
            origin = ORIGIN_PRESERVED

        entries.append(
            FootprintEntry(
                path=dest,
                source=item.source,
                sha256=sha256_hex(content),
                origin=origin,
            )
        )

    entries.sort(key=lambda row: row.path)
    return entries


def run_sync(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer sync``."""
    report = CommandReport()
    include_preserved = bool(getattr(args, "include_preserved", False))
    promote = bool(args.force and include_preserved)

    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="sync")
    config_path = resolve_config_path(repo_root, args.config)

    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    if not config_path.is_file():
        ctx.output.error("config missing: run `overseer init` first")
        return 2

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    try:
        validate_muse_working_dir(repo_root, config.vcs.muse.working_dir)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    lock_file = lock_path(repo_root)
    try:
        lock = read_version_lock(lock_file)
    except Exception as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 6

    try:
        rendered = resolve_footprint(config, kit=ctx.kit)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    living = living_doc_destinations(config)
    classified = classify_footprint(rendered, lock, repo_root)
    only_globs = list(args.only or [])

    in_scope = [
        row
        for row in classified
        if not only_globs or matches_glob(row.destination, only_globs)
    ]
    out_of_scope = [
        row
        for row in classified
        if only_globs and not matches_glob(row.destination, only_globs)
    ]

    for row in out_of_scope:
        if row.is_conflict:
            report.add_warning(
                f"out-of-scope conflict (not blocking): {row.destination} [{row.classification.value}]"
            )

    # Living-doc / origin:preserved paths are non-blocking unless promoting (§K6.4).
    blocking_conflicts = []
    for row in in_scope:
        preserved = _is_preserved_path(lock, row.destination, living)
        if preserved and not promote:
            if row.is_conflict or row.classification == Classification.KIT_UPDATED:
                report.add_warning(
                    f"preserved living doc (not blocking): {row.destination} [{row.classification.value}]"
                )
            continue
        if row.is_conflict:
            blocking_conflicts.append(row)

    report.data["classified"] = [
        {"path": row.destination, "status": row.classification.value}
        for row in classified
    ]

    show_diff = args.diff and not ctx.output.json_mode
    if show_diff:
        for row in classified:
            if row.classification == Classification.UNCHANGED:
                continue
            dest = repo_root / row.destination
            old = dest.read_bytes() if dest.is_file() else b""
            _emit_diff(ctx, row.destination, old, row.new_content)

    if blocking_conflicts and not args.force:
        ctx.output.error("refused: consumer-modified files without --force")
        for row in blocking_conflicts:
            ctx.output.error(f"  conflict: {row.destination} [{row.classification.value}]")
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        return 4

    writes_needed = []
    promoted: set[str] = set()
    for row in in_scope:
        preserved = _is_preserved_path(lock, row.destination, living)
        if preserved:
            if not promote:
                continue
            promoted.add(row.destination)
            dest = repo_root / row.destination
            on_disk = dest.read_bytes() if dest.is_file() else None
            if on_disk != row.new_content:
                writes_needed.append(row)
            continue
        if row.needs_write or (args.force and row.is_conflict):
            writes_needed.append(row)

    if not writes_needed and not promoted and lock.kit_version == kit_version():
        report.data["status"] = "already_current"
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        else:
            ctx.output.emit("already current")
        return 0

    if args.dry_run:
        report.data["dry_run"] = True
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        else:
            ctx.output.emit("dry-run: no files written")
        return 0

    if not args.yes and sys.stdin.isatty() and not ctx.output.json_mode:
        answer = input("Apply sync? [y/N]: ").strip().lower()
        if answer not in {"y", "yes"}:
            ctx.output.emit("aborted")
            return 0

    writes: dict[str, bytes] = {}
    try:
        for row in writes_needed:
            atomic_write_bytes(repo_root / row.destination, row.new_content)
            writes[row.destination] = row.new_content

        entries = _build_post_sync_entries(
            lock=lock,
            rendered=rendered,
            only_globs=only_globs,
            writes=writes,
            promoted=promoted,
            retain_preserved=True,
        )
        if promoted:
            by_path = {e.path: e for e in entries}
            for dest in promoted:
                item = next(i for i in rendered if i.destination == dest)
                on_disk_path = repo_root / dest
                if dest in writes:
                    content = writes[dest]
                elif on_disk_path.is_file():
                    content = on_disk_path.read_bytes()
                else:
                    content = item.content
                by_path[dest] = FootprintEntry(
                    path=dest,
                    source=item.source,
                    sha256=sha256_hex(content),
                    origin=ORIGIN_KIT,
                )
            entries = sorted(by_path.values(), key=lambda e: e.path)

        new_lock = build_version_lock_from_entries(
            kit_version=kit_version(),
            config_version=config.overseer_config_version,
            entries=entries,
            installed_at=lock.installed_at,
        )
        write_version_lock(lock_file, new_lock)
    except WriteFailure as exc:
        ctx.output.error(sanitize_text(str(exc), repo_root))
        return 5

    report.data["status"] = "synced"
    report.data["updated"] = [row.destination for row in writes_needed]
    report.data["promoted"] = sorted(promoted)
    if ctx.output.json_mode:
        ctx.output.emit_json(report.to_payload())
    else:
        ctx.output.emit("sync complete")
        for row in writes_needed:
            ctx.output.emit(f"  updated: {row.destination}")
        for dest in sorted(promoted):
            if dest not in {row.destination for row in writes_needed}:
                ctx.output.emit(f"  promoted: {dest}")
    return 0

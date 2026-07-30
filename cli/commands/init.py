"""``overseer init`` command (§K4.2 + §K6.4 ``--migrate``)."""

from __future__ import annotations

from argparse import Namespace
from enum import Enum
from pathlib import Path

from adapters.config import SUPPORTED_REGIMES, load_config
from adapters.errors import ConfigError
from cli.atomic import WriteFailure, atomic_write_text
from cli.config_gen import (
    config_dict_to_yaml,
    configs_equal,
    default_config_dict,
    detect_regime,
    load_config_from_dict,
)
from cli.context import CliContext
from cli.digest import sha256_hex
from cli.docs_paths import living_doc_destinations, validate_muse_working_dir
from cli.footprint import FootprintFile, resolve_footprint
from cli.footprint_writes import write_footprint_bytes
from cli.kn_r2 import KN_R2_DEST, evaluate_kn_r2
from cli.output import CommandReport
from cli.paths import PathEscapeError, confine_path, is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error, sanitize_text
from cli.version_lock import (
    ORIGIN_KIT,
    ORIGIN_PRESERVED,
    FootprintEntry,
    build_version_lock_from_entries,
    lock_path,
    read_version_lock,
    write_version_lock,
)


class MigrateClass(str, Enum):
    """Per-file migrate classification (§K6.4)."""

    SEED = "seed"
    UNCHANGED = "unchanged"
    PRESERVED = "preserved"
    UPDATED = "updated"
    CONFLICT = "conflict"


def _read_bytes_if_exists(path: Path) -> bytes | None:
    if path.is_file():
        return path.read_bytes()
    return None


def _footprint_matches(
    repo_root: Path,
    rendered,
    lock,
) -> bool:
    """Return True when on-disk footprint matches rendered content and lock manifest."""
    if lock is None:
        return False
    rendered_map = {item.destination: item for item in rendered}
    if len(lock.footprint) != len(rendered_map):
        return False
    for entry in lock.footprint:
        item = rendered_map.get(entry.path)
        if item is None:
            return False
        expected = entry.sha256
        on_disk = _read_bytes_if_exists(repo_root / entry.path)
        if on_disk is None or sha256_hex(on_disk) != expected:
            return False
        if entry.origin == ORIGIN_PRESERVED:
            continue
        if sha256_hex(item.content) != entry.sha256:
            return False
    return True


def _resolve_init_config(args: Namespace, repo_root: Path, config_path: Path) -> tuple[object, str]:
    """Determine config object and YAML text for init."""
    if args.from_config:
        from_path = Path(args.from_config).expanduser()
        if not from_path.is_absolute():
            from_path = (repo_root / from_path).resolve()
        else:
            from_path = from_path.resolve()
        text = from_path.read_text(encoding="utf-8")
        config = load_config(from_path)
        return config, text

    regime = args.regime
    if regime is None:
        regime = detect_regime(repo_root)
    if regime is None and not args.non_interactive:
        regime = input("Select regime [git-only|muse-only|muse+git-mirror]: ").strip()
    if regime is None or regime not in SUPPORTED_REGIMES:
        raise ConfigError("regime could not be determined (use --regime or --from-config)", str(config_path))

    repo_name = args.repo_name or repo_root.name
    docs_dir = args.docs_dir or "docs"
    data = default_config_dict(regime=regime, repo_name=repo_name, docs_dir=docs_dir)
    config = load_config_from_dict(data, str(config_path))
    return config, config_dict_to_yaml(data)


def _promote(args: Namespace) -> bool:
    return bool(getattr(args, "force", False) and getattr(args, "include_preserved", False))


def _classify_migrate(
    *,
    item: FootprintFile,
    existing: bytes | None,
    is_living: bool,
    promote: bool,
    kn_r2_pass: bool,
    force: bool,
    preserve_shared: bool = False,
) -> MigrateClass:
    """Classify one footprint destination under ``--migrate`` (§K6.4 + §PSA.3)."""
    if existing is None:
        return MigrateClass.SEED

    identical = existing == item.content
    if is_living:
        if promote:
            return MigrateClass.UPDATED  # promotion (write if differ; ownership if identical)
        if identical:
            return MigrateClass.UNCHANGED
        return MigrateClass.PRESERVED

    # Shared asset
    if identical:
        return MigrateClass.UNCHANGED
    if item.destination == KN_R2_DEST and kn_r2_pass:
        return MigrateClass.UPDATED
    # §PSA.3: consumer-owned shared assets stay on disk unless explicitly promoted
    if preserve_shared and not promote:
        return MigrateClass.PRESERVED
    if force:
        return MigrateClass.UPDATED
    return MigrateClass.CONFLICT


def run_init(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer init``."""
    report = CommandReport()
    migrate = bool(getattr(args, "migrate", False))
    include_preserved = bool(getattr(args, "include_preserved", False))
    preserve_shared = bool(getattr(args, "preserve_shared_assets", False))
    promote = _promote(args)

    if migrate and not args.non_interactive and not args.from_config and not args.regime:
        # §K6.4: require non-interactive for CI/fixtures OR from-config/regime
        pass  # regime/from-config checked below via fail-closed

    repo_root = resolve_repo_root(cwd=ctx.cwd, repo_arg=args.repo, command="init")
    config_path = resolve_config_path(repo_root, args.config)

    if not is_within_repo(repo_root, config_path):
        ctx.output.error("refused: config path outside repo root")
        return 4

    try:
        confine_path(repo_root, ".")
    except PathEscapeError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 4

    existing_config_path = config_path
    has_config = existing_config_path.is_file()
    existing_lock_path = lock_path(repo_root)
    has_lock = existing_lock_path.is_file()

    if has_config and not args.force:
        try:
            existing_config = load_config(existing_config_path)
        except ConfigError as exc:
            ctx.output.error(format_config_error(exc, repo_root))
            return 2

        try:
            existing_lock = read_version_lock(existing_lock_path) if has_lock else None
        except Exception as exc:
            report.data["refusal_reason"] = str(exc)
            ctx.output.error(f"existing install differs: {exc}")
            return 4

        try:
            planned_config, _planned_text = _resolve_init_config(args, repo_root, config_path)
        except ConfigError as exc:
            ctx.output.error(format_config_error(exc, repo_root))
            return 2

        try:
            validate_muse_working_dir(repo_root, planned_config.vcs.muse.working_dir)
        except ConfigError as exc:
            ctx.output.error(format_config_error(exc, repo_root))
            return 2

        try:
            rendered = resolve_footprint(planned_config, kit=ctx.kit)
        except ConfigError as exc:
            ctx.output.error(format_config_error(exc, repo_root))
            return 2

        if configs_equal(existing_config, planned_config) and _footprint_matches(
            repo_root, rendered, existing_lock
        ):
            report.data["status"] = "already_current"
            if ctx.output.json_mode:
                ctx.output.emit_json(report.to_payload())
            else:
                ctx.output.emit("already current")
            return 0

        report.data["refusal_reason"] = "existing install differs"
        ctx.output.error("refused: existing config or footprint differs (use --force)")
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        return 4

    if migrate and not args.from_config and not args.regime and args.non_interactive:
        # Fail closed if guessing required
        try:
            _resolve_init_config(args, repo_root, config_path)
        except ConfigError:
            ctx.output.error("migrate requires --from-config or --regime in --non-interactive mode")
            return 2

    try:
        config, config_text = _resolve_init_config(args, repo_root, config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    try:
        validate_muse_working_dir(repo_root, config.vcs.muse.working_dir)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    try:
        rendered = resolve_footprint(config, kit=ctx.kit)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    if not migrate:
        return _run_greenfield_init(
            args=args,
            ctx=ctx,
            report=report,
            repo_root=repo_root,
            config_path=config_path,
            config=config,
            config_text=config_text,
            rendered=rendered,
            existing_lock_path=existing_lock_path,
            has_lock=has_lock,
            preserve_shared=preserve_shared,
            promote=promote,
        )

    return _run_migrate_init(
        args=args,
        ctx=ctx,
        report=report,
        repo_root=repo_root,
        config_path=config_path,
        config=config,
        config_text=config_text,
        rendered=rendered,
        existing_lock_path=existing_lock_path,
        has_lock=has_lock,
        promote=promote,
        include_preserved=include_preserved,
        preserve_shared=preserve_shared,
    )


def _run_greenfield_init(
    *,
    args: Namespace,
    ctx: CliContext,
    report: CommandReport,
    repo_root: Path,
    config_path: Path,
    config,
    config_text: str,
    rendered: list[FootprintFile],
    existing_lock_path: Path,
    has_lock: bool,
    preserve_shared: bool = False,
    promote: bool = False,
) -> int:
    """§K4.2 greenfield init + §PSA.4 shared-asset preserve."""
    living = living_doc_destinations(config)
    conflicts: list[str] = []
    preserved_shared: list[str] = []
    preserved_bytes: dict[str, bytes] = {}

    for item in rendered:
        dest = repo_root / item.destination
        if not dest.is_file():
            continue
        existing = dest.read_bytes()
        if existing == item.content:
            continue
        is_living = item.destination in living
        if preserve_shared and not is_living and not promote:
            preserved_shared.append(item.destination)
            preserved_bytes[item.destination] = existing
            continue
        conflicts.append(item.destination)

    if conflicts and not args.force:
        report.data["conflicts"] = conflicts
        ctx.output.error("refused: footprint conflicts without --force")
        for path in conflicts:
            ctx.output.error(f"  conflict: {path}")
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        return 4

    plan = {
        "config": (
            str(config_path.relative_to(repo_root))
            if config_path.is_relative_to(repo_root)
            else ".overseer/config.yaml"
        ),
        "files": [item.destination for item in rendered],
        "conflicts": conflicts,
        "preserved_shared": preserved_shared,
    }
    report.data["plan"] = plan

    if args.dry_run:
        report.data["dry_run"] = True
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        else:
            ctx.output.emit("dry-run: no files written")
            for item in rendered:
                if item.destination in preserved_bytes:
                    ctx.output.emit(f"  would preserve: {item.destination}")
                else:
                    ctx.output.emit(f"  would write: {item.destination}")
        return 0

    prior_installed_at = None
    if has_lock:
        try:
            prior_installed_at = read_version_lock(existing_lock_path).installed_at
        except Exception:
            prior_installed_at = None

    from cli.kit_root import kit_version

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(config_path, config_text)
        entries: list[FootprintEntry] = []
        for item in sorted(rendered, key=lambda row: row.destination):
            if item.destination in preserved_bytes:
                content = preserved_bytes[item.destination]
                origin = ORIGIN_PRESERVED
            else:
                write_footprint_bytes(
                    repo_root / item.destination, item.content, destination=item.destination
                )
                content = item.content
                origin = ORIGIN_KIT
            entries.append(
                FootprintEntry(
                    path=item.destination,
                    source=item.source,
                    sha256=sha256_hex(content),
                    origin=origin,
                )
            )
        from cli.version_lock import utc_now_iso

        lock = build_version_lock_from_entries(
            kit_version=kit_version(),
            config_version=config.overseer_config_version,
            entries=entries,
            installed_at=prior_installed_at or utc_now_iso(),
        )
        write_version_lock(existing_lock_path, lock)
    except WriteFailure as exc:
        ctx.output.error(sanitize_text(str(exc), repo_root))
        return 5

    report.data["status"] = "initialized"
    report.data["preserved"] = preserved_shared
    report.data["lock"] = lock.to_dict()
    if ctx.output.json_mode:
        ctx.output.emit_json(report.to_payload())
    else:
        ctx.output.emit("init complete")
        for item in rendered:
            if item.destination in preserved_bytes:
                ctx.output.emit(f"  preserved: {item.destination}")
            else:
                ctx.output.emit(f"  wrote: {item.destination}")
    return 0


def _run_migrate_init(
    *,
    args: Namespace,
    ctx: CliContext,
    report: CommandReport,
    repo_root: Path,
    config_path: Path,
    config,
    config_text: str,
    rendered: list[FootprintFile],
    existing_lock_path: Path,
    has_lock: bool,
    promote: bool,
    include_preserved: bool,
    preserve_shared: bool = False,
) -> int:
    """§K6.4 ``init --migrate`` living-doc preserve + §PSA.3 shared-asset preserve."""
    living = living_doc_destinations(config)
    kn_r2_pass = False
    kn_r2_rendered: bytes | None = None
    kn_r2_dest_present = (repo_root / KN_R2_DEST).is_file()
    if kn_r2_dest_present:
        kn_r2_pass, kn_r2_rendered, kn_r2_diff = evaluate_kn_r2(repo_root, config, kit=ctx.kit)
        if not kn_r2_pass and kn_r2_diff:
            report.add_warning("KN-R2 semantic parity failed; rule remains a shared-asset conflict")
            if args.verbose if hasattr(args, "verbose") else False:
                ctx.output.error(kn_r2_diff)

    classifications: dict[str, MigrateClass] = {}
    write_plan: dict[str, bytes] = {}
    origins: dict[str, str] = {}
    lock_bytes: dict[str, bytes] = {}
    conflicts: list[str] = []
    preserved: list[str] = []
    created: list[str] = []
    unchanged: list[str] = []
    updated: list[str] = []

    for item in rendered:
        dest_path = repo_root / item.destination
        existing = _read_bytes_if_exists(dest_path)
        is_living = item.destination in living
        content = item.content
        if item.destination == KN_R2_DEST and kn_r2_pass and kn_r2_rendered is not None:
            content = kn_r2_rendered
            item_for_class = FootprintFile(
                destination=item.destination,
                source=item.source,
                content=content,
            )
        else:
            item_for_class = item

        klass = _classify_migrate(
            item=item_for_class,
            existing=existing,
            is_living=is_living,
            promote=promote,
            kn_r2_pass=kn_r2_pass and item.destination == KN_R2_DEST,
            force=bool(args.force),
            preserve_shared=preserve_shared,
        )
        classifications[item.destination] = klass

        if klass == MigrateClass.CONFLICT:
            conflicts.append(item.destination)
            continue

        if klass == MigrateClass.SEED:
            write_plan[item.destination] = content
            created.append(item.destination)
            lock_bytes[item.destination] = content
            origins[item.destination] = ORIGIN_PRESERVED if is_living else ORIGIN_KIT
        elif klass == MigrateClass.UNCHANGED:
            unchanged.append(item.destination)
            assert existing is not None
            lock_bytes[item.destination] = existing
            origins[item.destination] = ORIGIN_PRESERVED if is_living else ORIGIN_KIT
        elif klass == MigrateClass.PRESERVED:
            preserved.append(item.destination)
            assert existing is not None
            lock_bytes[item.destination] = existing
            origins[item.destination] = ORIGIN_PRESERVED
        elif klass == MigrateClass.UPDATED:
            updated.append(item.destination)
            if is_living and promote:
                if existing != content:
                    write_plan[item.destination] = content
                    lock_bytes[item.destination] = content
                else:
                    assert existing is not None
                    lock_bytes[item.destination] = existing
                origins[item.destination] = ORIGIN_KIT
            else:
                write_plan[item.destination] = content
                lock_bytes[item.destination] = content
                origins[item.destination] = ORIGIN_KIT

    # include_preserved without force is a no-op for living-doc writes (already handled:
    # promote requires both flags).
    _ = include_preserved

    if conflicts:
        report.data["conflicts"] = conflicts
        ctx.output.error("refused: shared-asset conflicts without --force")
        for path in conflicts:
            ctx.output.error(f"  conflict: {path}")
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        return 4

    report.data["created"] = created
    report.data["preserved"] = preserved
    report.data["unchanged"] = unchanged
    report.data["updated"] = updated
    report.data["conflicts"] = []
    report.data["classifications"] = {k: v.value for k, v in classifications.items()}

    if args.dry_run:
        report.data["dry_run"] = True
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        else:
            ctx.output.emit("dry-run: no files written")
            for path in created:
                ctx.output.emit(f"  would seed: {path}")
            for path in preserved:
                ctx.output.emit(f"  would preserve: {path}")
            for path in updated:
                ctx.output.emit(f"  would update: {path}")
        return 0

    prior_installed_at = None
    if has_lock:
        try:
            prior_installed_at = read_version_lock(existing_lock_path).installed_at
        except Exception:
            prior_installed_at = None

    from cli.kit_root import kit_version

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(config_path, config_text)
        for dest, content in write_plan.items():
            write_footprint_bytes(repo_root / dest, content, destination=dest)

        from cli.version_lock import utc_now_iso

        entries: list[FootprintEntry] = []
        for item in sorted(rendered, key=lambda row: row.destination):
            dest = item.destination
            content = lock_bytes[dest]
            entries.append(
                FootprintEntry(
                    path=dest,
                    source=item.source,
                    sha256=sha256_hex(content),
                    origin=origins[dest],
                )
            )
        lock = build_version_lock_from_entries(
            kit_version=kit_version(),
            config_version=config.overseer_config_version,
            entries=entries,
            installed_at=prior_installed_at or utc_now_iso(),
        )
        write_version_lock(existing_lock_path, lock)
    except WriteFailure as exc:
        ctx.output.error(sanitize_text(str(exc), repo_root))
        return 5

    report.data["status"] = "migrated"
    report.data["lock"] = lock.to_dict()
    if ctx.output.json_mode:
        ctx.output.emit_json(report.to_payload())
    else:
        ctx.output.emit("migrate init complete")
        for path in created:
            ctx.output.emit(f"  seeded: {path}")
        for path in preserved:
            ctx.output.emit(f"  preserved: {path}")
        for path in updated:
            ctx.output.emit(f"  updated: {path}")
        for path in unchanged:
            ctx.output.emit(f"  unchanged: {path}")
    return 0

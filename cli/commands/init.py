"""``overseer init`` command (§K4.2)."""

from __future__ import annotations

from pathlib import Path

from adapters.config import SUPPORTED_REGIMES, load_config
from adapters.errors import ConfigError
from cli.atomic import WriteFailure, atomic_write_bytes, atomic_write_text
from cli.config_gen import (
    config_dict_to_yaml,
    configs_equal,
    default_config_dict,
    detect_regime,
    load_config_from_dict,
)
from cli.context import CliContext
from cli.footprint import footprint_tuples, resolve_footprint
from cli.output import CommandReport
from cli.paths import PathEscapeError, confine_path, is_within_repo, resolve_config_path, resolve_repo_root
from cli.sanitize import format_config_error, sanitize_text
from cli.version_lock import build_version_lock, lock_path, read_version_lock, write_version_lock


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
        from cli.digest import sha256_hex

        if sha256_hex(item.content) != entry.sha256:
            return False
        on_disk = _read_bytes_if_exists(repo_root / entry.path)
        if on_disk is None or sha256_hex(on_disk) != entry.sha256:
            return False
    return True


def _resolve_init_config(args: Namespace, repo_root: Path, config_path: Path) -> tuple[object, str]:
    """Determine config object and YAML text for init."""
    if args.from_config:
        from_path = Path(args.from_config).expanduser()
        if not from_path.is_absolute():
            from_path = repo_root / from_path
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


def run_init(args: Namespace, ctx: CliContext) -> int:
    """Execute ``overseer init``."""
    report = CommandReport()
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

    try:
        config, config_text = _resolve_init_config(args, repo_root, config_path)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    try:
        rendered = resolve_footprint(config, kit=ctx.kit)
    except ConfigError as exc:
        ctx.output.error(format_config_error(exc, repo_root))
        return 2

    conflicts: list[str] = []
    for item in rendered:
        dest = repo_root / item.destination
        if dest.is_file():
            existing = dest.read_bytes()
            if existing != item.content:
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
        "config": str(config_path.relative_to(repo_root)) if config_path.is_relative_to(repo_root) else ".overseer/config.yaml",
        "files": [item.destination for item in rendered],
        "conflicts": conflicts,
    }
    report.data["plan"] = plan

    if args.dry_run:
        report.data["dry_run"] = True
        if ctx.output.json_mode:
            ctx.output.emit_json(report.to_payload())
        else:
            ctx.output.emit("dry-run: no files written")
            for item in rendered:
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
        for item in rendered:
            atomic_write_bytes(repo_root / item.destination, item.content)
        lock = build_version_lock(
            kit_version=kit_version(),
            config_version=config.overseer_config_version,
            footprint=footprint_tuples(rendered),
            prior_installed_at=prior_installed_at,
        )
        write_version_lock(existing_lock_path, lock)
    except WriteFailure as exc:
        ctx.output.error(sanitize_text(str(exc), repo_root))
        return 5

    report.data["status"] = "initialized"
    report.data["lock"] = lock.to_dict()
    if ctx.output.json_mode:
        ctx.output.emit_json(report.to_payload())
    else:
        ctx.output.emit("init complete")
        for item in rendered:
            ctx.output.emit(f"  wrote: {item.destination}")
    return 0

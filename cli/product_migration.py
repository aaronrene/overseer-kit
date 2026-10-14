"""Reviewed schema migration and confined, config-last foundation asset updates.

This is deliberately a collection of per-file atomic replacements, not a
transaction. A reviewed plan and byte-exact backups make interrupted progress
inspectable and retryable without guessing which version a file contains.
"""
from __future__ import annotations

import base64
import copy
import difflib
import fnmatch
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import uuid
from argparse import Namespace

from cli.v1_io import Refusal, atomic, confined, digest, read

CONFIG = ".overseer/config.yaml"
NEXT = "docs/NEXT.md"
LOCK = ".overseer/version.lock"
LAUNCHER = ".overseer/bin/ok"
HOOKS = (".cursor/hooks.json", ".cursor/hooks/session-start-next.sh",
         ".cursor/hooks/session-end-closeout.sh", ".overseer/instructions/bookends.md")


def _json(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def _plan_shape(plan):
    required = {"plan_version", "operation", "source_schema", "repository", "source_config_sha256",
                "normalized_config", "field_map", "diagnostics", "refresh_runtime", "context", "assets",
                "protected", "classification", "legacy_prompt_drafts", "next", "apply_supported"}
    if not isinstance(plan, dict) or set(plan) != required:
        raise Refusal("migration_plan_invalid")
    for field in ("normalized_config", "repository", "context"):
        if not isinstance(plan[field], dict):
            raise Refusal("migration_plan_invalid")
    for field in ("assets", "protected", "field_map", "diagnostics", "classification", "legacy_prompt_drafts"):
        if not isinstance(plan[field], (list, tuple)):
            raise Refusal("migration_plan_invalid")
    if (type(plan["refresh_runtime"]) is not bool or type(plan["apply_supported"]) is not bool or
            not isinstance(plan["source_config_sha256"], str) or
            not re.fullmatch(r"[0-9a-f]{64}", plan["source_config_sha256"])):
        raise Refusal("migration_plan_invalid")

    def snapshot(row):
        if (not isinstance(row, dict) or set(row) != {"path", "sha256", "mode"} or
                not isinstance(row["path"], str) or not isinstance(row["sha256"], str) or
                not re.fullmatch(r"absent|[0-9a-f]{64}", row["sha256"]) or
                ((row["sha256"] == "absent") != (row["mode"] is None)) or
                (row["mode"] is not None and (type(row["mode"]) is not int or not 0 <= row["mode"] <= 0o7777))):
            raise Refusal("migration_plan_snapshot_invalid")

    for row in plan["protected"]:
        snapshot(row)
    for row in plan["assets"]:
        if (not isinstance(row, dict) or set(row) != {"path", "before", "after", "mode", "content_b64"} or
                not isinstance(row["path"], str) or not isinstance(row["after"], str) or
                not re.fullmatch(r"[0-9a-f]{64}", row["after"]) or type(row["mode"]) is not int or
                not 0 <= row["mode"] <= 0o7777 or not isinstance(row["content_b64"], str)):
            raise Refusal("migration_plan_asset_invalid")
        snapshot(row["before"])


def _snapshot(root, path):
    target = confined(root, path, missing_parents=True)
    body = read(root, path, missing=True)
    return {"path": path, "sha256": "absent" if body is None else digest(body),
            "mode": None if body is None else stat.S_IMODE(target.stat().st_mode)}


def _same(root, row):
    return _snapshot(root, row["path"]) == row


def _lock_entries(root):
    from cli.v1 import decode
    raw = read(root, LOCK, missing=True)
    if raw is None:
        return {}
    value = decode(raw)
    if not isinstance(value, dict) or not isinstance(value.get("footprint"), list):
        raise Refusal("footprint_lock_invalid")
    entries = {}
    for entry in value["footprint"]:
        if (not isinstance(entry, dict) or not isinstance(entry.get("path"), str)
                or entry["path"] in entries or entry.get("origin", "kit") not in ("kit", "preserved")
                or not isinstance(entry.get("sha256"), str)):
            raise Refusal("footprint_lock_entry_invalid")
        confined(root, entry["path"], missing_parents=True)
        entries[entry["path"]] = entry
    return entries


def _bound_launcher(body, root, config):
    """B's launcher template is retained exactly; custom additions are user-owned."""
    from cli import v1
    return body is not None and body == v1.launcher(root, config["repo"]["id"])


def _bounded_hook_assets(root):
    """Exact B templates: explicit sync can upgrade these without taking custom assets."""
    from cli.product_bookends import hook_script
    return {".cursor/hooks/session-start-next.sh": hook_script(root),
            ".cursor/hooks/session-end-closeout.sh": hook_script(root),
            ".cursor/hooks.json": (json.dumps({"version": 1, "hooks": {
                "sessionStart": [{"command": str(root / ".cursor/hooks/session-start-next.sh")}],
                "stop": [{"command": str(root / ".cursor/hooks/session-end-closeout.sh")}],
            }}, indent=2) + "\n").encode()}


def classify_assets(root, mapping, config):
    """D's three-way classification, with confined reads and preserved origins.

    Full legacy footprint rows remain visible; this wave only updates its
    explicitly requested launcher/bookend assets. Unknown assets stay owned by
    the repository. Living documents are never update candidates here.
    """
    entries = _lock_entries(root)
    bounded_hooks = _bounded_hook_assets(root) if any(path in HOOKS for path in mapping) else {}
    rows = []
    for path, body in sorted(mapping.items()):
        old = read(root, path, missing=True)
        entry = entries.get(path, {})
        baseline = entry.get("sha256", "").removeprefix("sha256:")
        current = "absent" if old is None else digest(old)
        after = digest(body)
        if old is None:
            classification = "missing"
        elif entry.get("origin") == "preserved":
            classification = "preserved"
        elif old == body:
            classification = "unchanged"
        elif (current == baseline or (path == LAUNCHER and _bound_launcher(old, root, config))
              or (path in bounded_hooks and old == bounded_hooks[path])):
            classification = "kit-updated"
        elif after == baseline:
            classification = "consumer-modified"
        else:
            classification = "both-changed"
        rows.append({"path": path, "classification": classification,
                     "origin": entry.get("origin", "unrecorded"),
                     "before": current, "after": after})
    return rows


def _document_paths(config):
    base = config["repo"].get("root_relative_docs", "docs")
    docs = config.get("docs", {})
    paths = {NEXT}
    for field in ("handover", "roadmap", "coordination", "standing_decisions"):
        if docs.get(field):
            paths.add((Path(base) / docs[field]).as_posix())
    for lane in (docs.get("lanes") or {}).values():
        for field in ("handover", "roadmap"):
            if lane.get(field):
                paths.add((Path(base) / lane[field]).as_posix())
    return paths


def inventory(root, config):
    paths = _document_paths(config) | set(_lock_entries(root)) | {LOCK, ".overseer/ledger.jsonl"}
    for section, fields in {
        "checkpoints": ("policy", "active_manifest", "progress", "orchestrator"),
        "honesty": ("ledger", "roles_file", "ci_reexecutor"),
        "model_routing": ("policy",), "workspace": ("manifest",),
        "close_ritual": ("consumer_verify_script",),
    }.items():
        values = config.get(section) or {}
        for field in fields:
            if values.get(field):
                paths.add(values[field])
    for extension in config.get("extensions") or []:
        paths.add(extension["config_path"])
    for path in (config.get("close_ritual") or {}).get("require_paths") or []:
        target = root / path
        if target.is_dir() and not target.is_symlink():
            for parent, dirs, files in os.walk(target, followlinks=False):
                if any((Path(parent) / name).is_symlink() for name in dirs):
                    raise Refusal("path_symlink")
                paths.update((Path(parent) / name).relative_to(root).as_posix() for name in files)
        else:
            paths.add(path)
    # Inventory custom policy, rule and skill files, including unrecorded ones.
    for prefix in (".overseer/policy", ".cursor/rules", ".cursor/skills", ".claude/skills"):
        directory = root / prefix
        if directory.is_symlink():
            raise Refusal("path_symlink")
        if directory.exists():
            for parent, dirs, files in os.walk(directory, followlinks=False):
                for name in dirs:
                    if (Path(parent) / name).is_symlink():
                        raise Refusal("path_symlink")
                paths.update((Path(parent) / name).relative_to(root).as_posix() for name in files)
    return [_snapshot(root, path) for path in sorted(paths)]


def _legacy_drafts(root, config):
    """Migration-only extraction: proposals are never published or executed."""
    drafts = []
    for path in sorted(_document_paths(config) - {NEXT}):
        body = read(root, path, missing=True)
        if body is None:
            continue
        try:
            text = body.decode("utf-8")
        except UnicodeError:
            raise Refusal("living_document_encoding_invalid") from None
        pattern = r"(?m)^### Paste-ready prompt[^\n]*\n(?:\s*\n)*(`{3,}|~{3,})[^\n]*\n(.*?)^\1[ \t]*$"
        for match in re.finditer(pattern, text, re.DOTALL | re.MULTILINE):
            drafts.append({"source": path, "text": match.group(2),
                           "sha256": digest(match.group(2).encode()),
                           "publication": "operator acceptance and next-write --expect-next absent required"})
    if read(root, NEXT, missing=True) is None and len({d["sha256"] for d in drafts}) > 1:
        raise Refusal("conflicting_legacy_prompts")
    return drafts


def _context(root):
    from cli import v1
    from cli.product_config import normalize
    config = normalize(read(root, CONFIG), root=root).data
    if config['vcs']['canonical'] == 'muse':
        state = v1.revision(root, config)
        return {'root': str(root), 'branch': state.branch, 'head': state.head,
                'source_id': state.source_id, 'runtime': v1.runtime()}
    if Path(v1.git(root, 'rev-parse', '--show-toplevel')).resolve(strict=True) != root:
        raise Refusal('migration_context_changed')
    return {"root": str(root), "branch": v1.branch(root), "head": v1.head(root),
            "runtime": v1.runtime()}


def _check_context(root, captured, allowed_config):
    from cli import v1
    if (root.resolve(strict=True) != root or
            _context(root) != captured):
        raise Refusal("migration_context_changed")
    if digest(read(root, CONFIG)) not in allowed_config:
        raise Refusal("migration_config_changed")


def _updates(root, mapping):
    updates = []
    for path, data in mapping.items():
        before = _snapshot(root, path)
        mode = (before["mode"] if path in (CONFIG, ".gitignore", ".museignore") and before["mode"] is not None else
                0o755 if path.endswith(".sh") or path.endswith("/ok") else 0o644)
        if before["sha256"] != digest(data) or before["mode"] != mode:
            updates.append({"path": path, "before": before, "after": digest(data),
                            "mode": mode, "content_b64": base64.b64encode(data).decode()})
    return updates


def apply_mapping(root, mapping, *, check_context, dry_run=False):
    """Preflight all targets before taking the same directory lock as migration."""
    updates = _updates(root, mapping)
    if dry_run:
        return [row["path"] for row in updates]
    fd = os.open(root / ".overseer", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        check_context()
        for row in updates:
            if not _same(root, row["before"]):
                raise Refusal("stale_write: " + row["path"])
        for row in updates:
            atomic(root, row["path"], base64.b64decode(row["content_b64"]),
                   expected=row["before"]["sha256"], mode=row["mode"], before_replace=check_context)
    except (Refusal, OSError) as exc:
        completed = [row["path"] for row in updates if _snapshot(root, row["path"]) ==
                     {"path": row["path"], "sha256": row["after"], "mode": row["mode"]}]
        if completed:
            reason = str(exc) if isinstance(exc, Refusal) else type(exc).__name__
            raise Refusal("partial_asset_update: " + ",".join(completed) + "; " + reason +
                          "; config is last; rerun explicit sync after resolving drift") from exc
        raise
    finally:
        os.close(fd)
    return [row["path"] for row in updates]


def build_plan(root, args):
    from cli import v1
    from cli.product_config import normalize
    original = read(root, CONFIG)
    # Stable proposed UUID makes repeated dry runs reviewable. It is persisted
    # only by the explicitly accepted initialization/migration plan.
    proposed = str(uuid.uuid5(uuid.NAMESPACE_URL, str(root) + ":" + digest(original)))
    unbound = normalize(original, root=root, runtime=v1.runtime())
    identity = unbound.data["repo"].get("id") or proposed
    model = normalize(original, root=root, runtime=v1.runtime(), bind=True, identity=identity,
                      lane=getattr(args, "lane", None), model=getattr(args, "model", None))
    config = copy.deepcopy(model.data)
    if getattr(args, "repo_name", None) not in (None, config["repo"]["name"]):
        raise Refusal("migration_repo_name_change_requires_explicit_resolution")
    if getattr(args, "regime", None) not in (None, config["vcs"]["regime"]):
        raise Refusal("authority_change_requires_adopt")
    if getattr(args, "refresh_runtime", False):
        config["runtime"] = v1.runtime()
    if getattr(args, "bound_id", None) not in (None, identity):
        raise Refusal("launcher_identity_mismatch")
    launcher = read(root, LAUNCHER, missing=True)
    if launcher is not None and not _bound_launcher(launcher, root, config):
        raise Refusal("migration_launcher_binding_conflict")
    # Preserve the selected authority and verify its native binding when available.
    git_authority = config["vcs"]["canonical"] == "git"
    current_next = read(root, NEXT, missing=True)
    available = git_authority or bool(config['vcs']['muse'].get('binding'))
    if available and current_next is not None:
        observed = v1.capture_context(root, original, config)
        for lane in config['docs']['lanes']:
            # A missing lane is visible at read time, and is not invented by migration.
            meta, body = v1.parse_next(current_next)
            if (meta['schema'] == 3 and lane not in meta['entries']) or (meta['schema'] != 3 and meta['lane'] != lane):
                continue
            v1.validate_next(root, config, current_next, Namespace(lane=lane), context=observed, freshness=False)
    mapping = v1.assets(root, config, False) if available else {}
    if getattr(args, "hooks", False):
        raise Refusal("migration_does_not_install_existing_repository_hooks")
    mapping[CONFIG] = v1.encode(config)
    updates = _updates(root, mapping)
    updated_paths = {row["path"] for row in updates}
    classifications = classify_assets(root, {k: v for k, v in mapping.items() if k != CONFIG}, config)
    for row in classifications:
        if row["classification"] == "preserved" and row["path"] in updated_paths:
            raise Refusal("migration_preserved_asset_requires_resolution: " + row["path"])
    protected_map = {row["path"]: row for row in inventory(root, config)}
    protected_map.update({path: _snapshot(root, path) for path in mapping if path not in updated_paths})
    protected = [row for path, row in sorted(protected_map.items()) if path not in updated_paths]
    plan = {"plan_version": 1, "operation": "schema-3-migration", "source_schema": model.source_schema,
            "repository": config["repo"], "source_config_sha256": digest(original),
            "normalized_config": config, "field_map": model.field_map,
            "diagnostics": list(model.diagnostics), "refresh_runtime": bool(getattr(args, "refresh_runtime", False)),
            "context": _context(root) if available else {"root": str(root), "runtime": v1.runtime(),
                "authority": "muse", "unavailable": "muse_binding_required"},
            "assets": updates, "protected": protected,
            "classification": classifications,
            "legacy_prompt_drafts": _legacy_drafts(root, config),
            "next": "preserved byte-for-byte; accepted drafts publish only through next-write",
            "apply_supported": available and config["runtime"] == v1.runtime()}
    if not available:
        plan['diagnostics'].append('Muse authority preserved; apply requires explicit native binding')
    if config["runtime"] != v1.runtime():
        plan["diagnostics"].append("Runtime changed: repeat dry-run with explicit --refresh-runtime")
    return plan


def _apply_plan(root, args, plan):
    from cli import v1
    from cli.product_config import normalize
    _plan_shape(plan)
    expected_plan = getattr(args, "expect_plan", None)
    if expected_plan != digest(_json(plan)):
        raise Refusal("migration_plan_digest_mismatch")
    if getattr(args, "expect_config", None) != plan.get("source_config_sha256"):
        raise Refusal("migration_expected_config_mismatch")
    if plan.get("plan_version") != 1 or plan.get("operation") != "schema-3-migration":
        raise Refusal("migration_plan_invalid")
    if plan.get("context", {}).get("root") != str(root):
        raise Refusal("migration_repository_mismatch")
    if not plan.get("apply_supported"):
        raise Refusal("migration_apply_unavailable: review plan diagnostics")
    backup = ".overseer/migrations/" + expected_plan
    original = read(root, CONFIG)
    resume = bool(getattr(args, "resume", False))
    if resume:
        saved = read(root, backup + "/files/" + CONFIG, missing=True)
        if saved is not None:
            original = saved
    if digest(original) != plan["source_config_sha256"]:
        raise Refusal("stale_write: " + CONFIG)
    target = plan["normalized_config"]
    validated = normalize(v1.encode(target), root=root, runtime=v1.runtime())
    if not validated.bound or target.get("schema") != 3 or validated.data != target:
        raise Refusal("migration_config_plan_invalid")
    proposed = normalize(original, root=root, runtime=v1.runtime(), bind=True,
                         identity=target["repo"]["id"], lane=target["context"]["lane"],
                         model=target["context"]["model"]).data
    if plan["refresh_runtime"]:
        proposed["runtime"] = v1.runtime()
    if proposed != target or target["runtime"] != v1.runtime():
        raise Refusal("migration_config_plan_changed")
    # JSON object order is not part of a reviewed plan's canonical digest.
    # Reproduce target YAML from the preserved source rather than an incidental
    # order chosen by a JSON viewer/editor.
    target = proposed
    if getattr(args, "bound_id", None) not in (None, target["repo"]["id"]):
        raise Refusal("launcher_identity_mismatch")
    approved = dict(v1.assets(root, target, False), **{CONFIG: v1.encode(target)})
    rows = plan["assets"]
    if not isinstance(rows, list) or len({row["path"] for row in rows}) != len(rows):
        raise Refusal("migration_asset_plan_invalid")
    for row in rows:
        if (row["path"] not in approved or row["before"]["path"] != row["path"] or
                base64.b64decode(row["content_b64"], validate=True) != approved[row["path"]] or
                row["after"] != digest(approved[row["path"]]) or
                row["mode"] != (0o755 if row["path"] == LAUNCHER else row["before"]["mode"])):
            raise Refusal("migration_asset_plan_changed")
    for path, content in approved.items():
        if path not in {row["path"] for row in rows}:
            captured = next((row for row in plan["protected"] if row["path"] == path), None)
            if captured is None or captured["sha256"] != digest(content) or not _same(root, captured):
                raise Refusal("migration_asset_plan_incomplete")
    if any(row["path"] == CONFIG for row in rows) and rows[-1]["path"] != CONFIG:
        raise Refusal("migration_config_must_be_last")
    allowed = {plan["source_config_sha256"]}
    if resume:
        allowed.add(digest(v1.encode(target)))

    def check():
        _check_context(root, plan["context"], allowed)
        for entry in plan["protected"]:
            if not _same(root, entry):
                raise Refusal("migration_protected_asset_changed: " + entry["path"])

    # No parent creation occurs until all destination and backup checks pass.
    for row in rows:
        current = _snapshot(root, row["path"])
        after = {"path": row["path"], "sha256": row["after"], "mode": row["mode"]}
        if current != row["before"] and not (resume and current == after):
            raise Refusal("stale_write: " + row["path"])
        confined(root, backup + "/files/" + row["path"], missing_parents=True)
    manifest_path = backup + "/manifest.json"
    manifest = _json({"plan_sha256": expected_plan, "plan": plan,
                      "rollback": "Quiesce commands; restore each files/ entry with its recorded mode; remove only originally absent assets; restore config last.",
                      "per_file_atomic_only": True})
    existing_manifest = read(root, manifest_path, missing=True)
    if existing_manifest is not None and existing_manifest != manifest:
        raise Refusal("migration_backup_manifest_mismatch")
    backup_rows = list(rows)
    if CONFIG not in {row["path"] for row in rows}:
        backup_rows.append({"path": CONFIG, "before": _snapshot(root, CONFIG)})
    backups = {}
    for row in backup_rows:
        if row["before"]["sha256"] == "absent":
            continue
        path = backup + "/files/" + row["path"]
        saved = read(root, path, missing=True)
        data = original if row["path"] == CONFIG else read(root, row["path"])
        if saved is not None:
            data = saved
        if digest(data) != row["before"]["sha256"]:
            raise Refusal("migration_backup_missing_original: " + row["path"])
        if saved is not None and digest(saved) != row["before"]["sha256"]:
            raise Refusal("migration_backup_mismatch")
        backups[path] = (data, row["before"]["mode"])
    check()
    changed = []
    fd = os.open(root / ".overseer", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        check()
        for row in rows:
            current = _snapshot(root, row["path"])
            after = {"path": row["path"], "sha256": row["after"], "mode": row["mode"]}
            if current != row["before"] and not (resume and current == after):
                raise Refusal("stale_write: " + row["path"])
        for path, (data, mode) in backups.items():
            saved = read(root, path, missing=True)
            atomic(root, path, data, expected="absent" if saved is None else digest(saved),
                   mode=mode, before_replace=check)
        atomic(root, manifest_path, manifest,
               expected="absent" if existing_manifest is None else digest(existing_manifest),
               before_replace=check)
        for row in rows:
            current = _snapshot(root, row["path"])
            after = {"path": row["path"], "sha256": row["after"], "mode": row["mode"]}
            if current == after:
                continue
            atomic(root, row["path"], approved[row["path"]], expected=row["before"]["sha256"],
                   mode=row["mode"], before_replace=check)
            changed.append(row["path"])
        allowed.add(digest(v1.encode(target)))
        check()
    except (Refusal, OSError) as exc:
        completed = [row["path"] for row in rows
                     if _snapshot(root, row["path"]) == {"path": row["path"], "sha256": row["after"], "mode": row["mode"]}]
        return {"ok": False, "partial": bool(completed), "completed": completed,
                "error": str(exc) if isinstance(exc, Refusal) else type(exc).__name__,
                "backup": backup, "resume": "Repeat the same --apply-plan, --expect-plan and --expect-config with --resume; drift still refuses"}
    finally:
        os.close(fd)
    return {"ok": True, "migrated": True, "changed": changed, "backup": backup,
            "repository": target["repo"], "config_sha256": digest(v1.encode(target)),
            "next": "preserved", "resumed": resume}


def migrate(root, args):
    if bool(getattr(args, "dry_run", False)) == bool(getattr(args, "apply_plan", None)):
        raise Refusal("migration_requires_dry_run_or_apply_plan")
    if args.dry_run:
        plan = build_plan(root, args)
        return {"ok": True, "dry_run": True, "plan_sha256": digest(_json(plan)), "plan": plan}
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Refusal("migration_plan_duplicate_key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise Refusal("migration_plan_invalid_constant")

    try:
        wrapper = json.loads(read(root, args.apply_plan).decode("utf-8"),
                             object_pairs_hook=unique, parse_constant=invalid_constant)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Refusal("migration_plan_json_invalid") from exc
    except RecursionError as exc:
        raise Refusal("migration_plan_nesting_invalid") from exc
    if not isinstance(wrapper, dict):
        raise Refusal("migration_plan_invalid")
    plan = wrapper.get("plan", wrapper)
    return _apply_plan(root, args, plan)


def sync(root, config, original, args):
    from cli import v1
    captured = v1.capture_context(root, original, config)
    runtime_observed = v1.runtime()
    updated = copy.deepcopy(config)
    updated["runtime"] = v1.runtime()
    mapping = v1.assets(root, updated, bool(getattr(args, "hooks", False)))
    selected = getattr(args, "only", None)
    if selected:
        selectors = [selected] if isinstance(selected, str) else selected
        # Discover only the foundation resources implemented in this wave.
        # Matching a hook destination is not permission to install its hook.
        available = v1.assets(root, updated, True)
        aliases = {"launcher": {LAUNCHER}, "hooks": set(HOOKS)}
        wanted = set()
        for selector in selectors:
            matches = aliases.get(selector)
            if matches is None:
                matches = {path for path in available if fnmatch.fnmatchcase(path, selector)}
            if not matches:
                raise Refusal("sync_only_no_matches: " + selector)
            if matches.intersection(HOOKS) and not getattr(args, "hooks", False):
                raise Refusal("sync_hooks_requires_explicit_hooks")
            wanted.update(matches)
        mapping = {path: body for path, body in available.items() if path in wanted}
    rows = classify_assets(root, mapping, config)
    preserved = []
    for row in rows:
        if row["classification"] in ("preserved", "consumer-modified", "both-changed"):
            if row["classification"] != "preserved" and not getattr(args, "preserve_modified", False):
                raise Refusal("sync_asset_modified: " + row["path"])
            preserved.append(row["path"])
            mapping.pop(row["path"], None)
    # Keep compatibility config bytes unless refresh is actually required; a
    # schema upgrade is explicit migration, never an incidental sync side effect.
    source = v1.decode(original)
    source["runtime"] = updated["runtime"]
    if source["runtime"] != v1.decode(original)["runtime"]:
        mapping[CONFIG] = v1.encode(source)
    changing = {row["path"] for row in _updates(root, mapping)}
    protected_map = {row["path"]: row for row in inventory(root, config)}
    protected_map.update({path: _snapshot(root, path) for path in mapping if path not in changing})
    protected = [row for path, row in protected_map.items() if path not in changing]

    def check():
        if (read(root, CONFIG) != original or v1.capture_context(root, original, config) != captured
                or v1.runtime() != runtime_observed):
            raise Refusal('sync_context_changed')
        for row in protected:
            if not _same(root, row):
                raise Refusal("sync_protected_asset_changed: " + row["path"])

    differences = {}
    if getattr(args, "diff", False):
        for path, body in mapping.items():
            prior = read(root, path, missing=True) or b""
            differences[path] = "".join(difflib.unified_diff(prior.decode().splitlines(True),
                body.decode().splitlines(True), fromfile=path, tofile=path + " (planned)"))
    changed = apply_mapping(root, mapping, check_context=check, dry_run=bool(args.dry_run))
    return {"ok": True, "repository": config["repo"], "changed": changed,
            "classification": rows, "preserved": preserved, "dry_run": bool(args.dry_run),
            "diff": differences, "next": "preserved"}

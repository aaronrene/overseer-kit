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

from cli.v1_io import Refusal, atomic as _atomic, confined, digest, read as _read, LIMIT

ASSET_LIMIT = 16 * 1024 * 1024


def read(root, relative, **kwargs):
    return _read(root, relative, limit=LIMIT if relative in (CONFIG, NEXT) else ASSET_LIMIT, **kwargs)


def atomic(root, relative, data, **kwargs):
    return _atomic(root, relative, data, limit=LIMIT if relative in (CONFIG, NEXT) else ASSET_LIMIT, **kwargs)

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


def _lock_entries(root, *, raw=None):
    from cli.v1 import decode
    if raw is None:
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


def classify_assets(root, mapping, config, *, read_asset=None, lock_entries=None):
    """D's three-way classification, with confined reads and preserved origins.

    Full legacy footprint rows remain visible; this wave only updates its
    explicitly requested launcher/bookend assets. Unknown assets stay owned by
    the repository. Living documents are never update candidates here.
    """
    entries = _lock_entries(root) if lock_entries is None else lock_entries
    read_asset = read_asset or (lambda path: read(root, path, missing=True))
    bounded_hooks = _bounded_hook_assets(root) if any(path in HOOKS for path in mapping) else {}
    rows = []
    for path, body in sorted(mapping.items()):
        old = read_asset(path)
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


def _legacy_consumer_owned(root, config, generated, entries):
    """Legacy kit records this runtime no longer generates, edited by the owner.

    They stay untouched and are re-recorded as preserved rather than left as
    a stale kit claim. Missing files keep their record so absence stays visible.
    """
    living = _document_paths(config)
    owned = []
    for path, entry in sorted(entries.items()):
        if (path in generated or path in living or path in (LOCK, CONFIG, NEXT)
                or entry.get("origin", "kit") != "kit"):
            continue
        body = read(root, path, missing=True)
        if body is not None and digest(body) != entry["sha256"].removeprefix("sha256:"):
            owned.append(path)
    return owned


def _migration_assets(root, config, mapping, classifications, *, lock_entries=None):
    """Keep owner collisions active and record their ownership for later sync."""
    from cli.product_footprint import with_lock
    entries = _lock_entries(root) if lock_entries is None else lock_entries
    preserved = _legacy_consumer_owned(root, config, set(mapping), entries)
    mapping = dict(mapping)
    for row in classifications:
        if row["classification"] == "missing":
            continue
        owner = (row["origin"] == "unrecorded" or
                 row["classification"] in ("preserved", "consumer-modified", "both-changed") or
                 (row["classification"] == "unchanged" and
                  bool(_updates(root, {row["path"]: mapping[row["path"]]}))))
        if row["path"] == LAUNCHER:
            # Exact operational bindings may be adopted; custom launchers and
            # preserved nonexecutable launchers still require explicit resolution.
            owner = row["classification"] == "preserved"
            if owner and _updates(root, {LAUNCHER: mapping[LAUNCHER]}):
                raise Refusal("migration_preserved_asset_requires_resolution: " + LAUNCHER)
        if owner:
            preserved.append(row["path"])
            mapping.pop(row["path"])
    return with_lock(root, mapping, config, preserved=preserved), preserved


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
    return drafts


def _context(root, config=None):
    """Observe the planned authority; a native binding being added is the plan's."""
    from cli import v1
    from cli.product_config import normalize
    if config is None:
        config = normalize(read(root, CONFIG), root=root).data
    if config['vcs']['canonical'] == 'muse':
        state = v1.revision(root, config)
        return {'root': str(root), 'branch': state.branch, 'head': state.head,
                'source_id': state.source_id, 'runtime': v1.runtime()}
    if Path(v1.git(root, 'rev-parse', '--show-toplevel')).resolve(strict=True) != root:
        raise Refusal('migration_context_changed')
    return {"root": str(root), "branch": v1.branch(root), "head": v1.head(root),
            "runtime": v1.runtime()}


def _check_context(root, captured, allowed_config, config=None):
    if (root.resolve(strict=True) != root or
            _context(root, config) != captured):
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


def _bind_native(root, config, python):
    """Explicitly bind an unbound Muse authority to its natively read source.

    Regime, branches, remotes and every other setting are retained; only the
    source identity, store and Muse runtime reported by the reader are added.
    """
    from cli import v1
    from cli.product_authority import bind_muse
    from cli.product_config import normalize
    if config["vcs"]["canonical"] != "muse":
        raise Refusal("git_does_not_use_muse_python")
    if config["vcs"]["muse"].get("binding"):
        raise Refusal("muse_binding_exists: change it with explicit adopt")
    bound = bind_muse(root, config, python)
    if (bound["vcs"]["regime"] != config["vcs"]["regime"] or
            normalize(v1.encode(bound), root=root).data != bound):
        raise Refusal("migration_config_plan_invalid")
    return bound


def _tracked_choice(root, config, args):
    from cli.product_authority import tracked_bindings
    tracked = tracked_bindings(root, config)
    if any(tracked.values()) and getattr(args, "tracked_bindings", None) != "preserve":
        raise Refusal("tracked_local_bindings: explicitly choose --tracked-bindings preserve or untrack separately")
    return tracked


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
    native = getattr(args, "muse_python", None) is not None
    tracked = {}
    if native:
        config = _bind_native(root, config, args.muse_python)
        tracked = _tracked_choice(root, config, args)
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
    classifications = classify_assets(root, mapping, config)
    preserved = []
    if available:
        mapping, preserved = _migration_assets(root, config, mapping, classifications)
    classified = {row["path"] for row in classifications}
    mapping[CONFIG] = v1.encode(config)
    updates = _updates(root, mapping)
    updated_paths = {row["path"] for row in updates}
    protected_map = {row["path"]: row for row in inventory(root, config)}
    protected_map.update({path: _snapshot(root, path) for path in preserved})
    protected_map.update({path: _snapshot(root, path) for path in mapping if path not in updated_paths})
    protected = [row for path, row in sorted(protected_map.items()) if path not in updated_paths]
    plan = {"plan_version": 1, "operation": "schema-3-migration", "source_schema": model.source_schema,
            "repository": config["repo"], "source_config_sha256": digest(original),
            "normalized_config": config, "field_map": model.field_map,
            "diagnostics": list(model.diagnostics), "refresh_runtime": bool(getattr(args, "refresh_runtime", False)),
            "context": _context(root, config) if available else {"root": str(root), "runtime": v1.runtime(),
                "authority": "muse", "unavailable": "muse_binding_required"},
            "assets": updates, "protected": protected,
            "classification": classifications,
            "legacy_prompt_drafts": _legacy_drafts(root, config),
            "next": "preserved byte-for-byte; accepted drafts publish only through next-write",
            "apply_supported": available and config["runtime"] == v1.runtime()}
    drafts = plan["legacy_prompt_drafts"]
    if drafts:
        plan["diagnostics"].append(
            f"historical_prompts_preserved: {len(drafts)} blocks / "
            f"{len({draft['sha256'] for draft in drafts})} distinct; none selected or activated; "
            "operator acceptance and next-write are separate")
    plan["diagnostics"].extend("legacy_kit_asset_consumer_owned: " + path
                               for path in preserved if path not in classified)
    if native:
        plan["diagnostics"].append("native_muse_binding_added: " + config["vcs"]["muse"]["binding"]["repo_id"])
        plan["diagnostics"].append("tracked_local_bindings_preserved: " + ", ".join(
            f"{kind}={len(paths)}" for kind, paths in sorted(tracked.items())) if any(tracked.values())
            else "tracked_local_bindings: none")
    if not available:
        plan['diagnostics'].append('Muse authority preserved; apply requires explicit native binding (--muse-python)')
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
    # A planned native binding is re-read now; a changed source never applies.
    native = bool(target["vcs"]["canonical"] == "muse" and target["vcs"]["muse"].get("binding")
                  and not proposed["vcs"]["muse"].get("binding"))
    if native:
        planned_python = target["vcs"]["muse"]["binding"]["runtime"]["python"]
        if getattr(args, "muse_python", None) not in (None, planned_python):
            raise Refusal("migration_muse_python_plan_mismatch")
        proposed = _bind_native(root, proposed, planned_python)
    elif getattr(args, "muse_python", None) is not None:
        raise Refusal("migration_muse_python_not_planned")
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
    if native:
        _tracked_choice(root, target, args)
    rows = plan["assets"]
    if not isinstance(rows, list) or len({row["path"] for row in rows}) != len(rows):
        raise Refusal("migration_asset_plan_invalid")
    snapshots = {row["path"]: row["before"] for row in rows}
    for row in plan["protected"]:
        if row["path"] in snapshots:
            raise Refusal("migration_asset_plan_invalid")
        snapshots[row["path"]] = row

    def before_asset(path):
        captured = snapshots.get(path)
        if captured is None:
            raise Refusal("migration_asset_plan_incomplete")
        if captured["sha256"] == "absent":
            return None
        data = read(root, backup + "/files/" + path, missing=True) if resume else None
        if data is None:
            data = read(root, path, missing=True)
        if data is None or digest(data) != captured["sha256"]:
            raise Refusal("migration_backup_missing_original: " + path)
        return data

    # Recompute ownership from the reviewed originals, including after a partial
    # apply has installed its new lock. A plan cannot relabel an owner collision.
    original_lock = before_asset(LOCK)
    entries = {} if original_lock is None else _lock_entries(root, raw=original_lock)
    generated = v1.assets(root, target, False)
    classifications = classify_assets(root, generated, target, read_asset=before_asset, lock_entries=entries)
    if classifications != plan["classification"]:
        raise Refusal("migration_classification_plan_changed")
    approved, preserved = _migration_assets(root, target, generated, classifications, lock_entries=entries)
    approved[CONFIG] = v1.encode(target)
    for row in rows:
        if (row["path"] not in approved or row["before"]["path"] != row["path"] or
                base64.b64decode(row["content_b64"], validate=True) != approved[row["path"]] or
                row["after"] != digest(approved[row["path"]]) or
                row["mode"] != (row['before']['mode'] if row['path'] in (CONFIG, '.gitignore', '.museignore') and row['before']['mode'] is not None else
                                0o755 if row['path'].endswith(('.sh', '/ok')) else 0o644)):
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
        _check_context(root, plan["context"], allowed, target)
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
    backup_rows.extend({"path": path, "before": snapshots[path]} for path in preserved)
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
    from cli.product_footprint import with_lock
    mapping = with_lock(root, mapping, updated, preserved=preserved)
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

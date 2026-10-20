"""Repository-bound context and the single confined canonical NEXT writer."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import sys
import uuid

import yaml

from cli.v1_io import LIMIT, Refusal, atomic, confined, digest, read
from cli.v1_revision import revision
from cli.v1_policy import local_path

VERSION = "1.0.0.dev1"
KIT = Path(__file__).resolve().parent.parent
CONFIG = ".overseer/config.yaml"
NEXT = "docs/NEXT.md"
KINDS = ("plan", "implement", "review", "maintain", "stop")
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
def runtime_files():
    """Owned code/resources used by normalization, migration and bound assets.

    Include complete cli/adapter source families so lazy helpers cannot escape
    the binding. Optional hosted configuration validators do not load transports.
    Paths and bytes both participate; adding or removing a source changes it.
    """
    paths = {"VERSION", "cli/ok", "cli/overseer", "scripts/muse-bridge-deploy.sh"}
    for directory in ("cli", "adapters", "tools"):
        paths.update(p.relative_to(KIT).as_posix() for p in (KIT / directory).rglob("*.py"))
    paths.update("tools/hosted_dashboard/" + p for p in
                 ("__init__.py", "config.py", "hosts.py", "validators.py"))
    for directory in ("cursor", "templates", "policy", "tools/app/static", "tools/hosted_dashboard/static"):
        paths.update(p.relative_to(KIT).as_posix() for p in (KIT / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    return tuple(sorted(paths))


RUNTIME_FILES = runtime_files()


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise Refusal("duplicate_or_invalid_key")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def decode(data: bytes):
    try:
        return yaml.load(data.decode("utf-8"), Loader=UniqueLoader)
    except (UnicodeError, yaml.YAMLError, ValueError, TypeError) as exc:
        raise Refusal("malformed_document") from exc


def encode(value) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True).encode()


def keys(value, required):
    if not isinstance(value, dict) or set(value) != set(required):
        raise Refusal("schema_keys_invalid")


def label(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 200 or any(ord(c) < 32 for c in value):
        raise Refusal("label_invalid")
    return value


def token(value):
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        raise Refusal("identifier_invalid")
    return value


def git(root: Path, *args: str, optional: bool = False, raw: bool = False):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(PATH="/usr/bin:/bin", GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL="/dev/null", LC_ALL="C")
    proc = subprocess.run(["/usr/bin/git", "-c", "core.fsmonitor=false", "-c",
                           "core.hooksPath=/dev/null", "-C", str(root), *args],
                          env=env, capture_output=True, text=not raw, timeout=15)
    if proc.returncode and not optional:
        raise Refusal("git_read_failed: " + args[0])
    if raw:
        return proc.stdout if proc.returncode == 0 else b""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def root_for(args) -> Path:
    cwd = Path.cwd().resolve()
    requested = Path(args.repo).expanduser().resolve(strict=True) if args.repo else cwd
    # A configured Muse/legacy root can be inspected without probing Git.
    # Never walk beyond the nearest repository boundary into a parent checkout.
    selected = requested
    if not args.repo:
        while not (selected / CONFIG).exists():
            if (selected / ".git").exists() or (selected / ".muse").exists() or selected == selected.parent:
                break
            selected = selected.parent
    if (selected / CONFIG).exists() or (selected / CONFIG).is_symlink():
        root = selected
    else:
        from cli.v1_revision import discover
        root = discover(requested)
    if args.repo and requested != root:
        raise Refusal("explicit_repo_must_be_root")
    if args.bound_root and root != Path(args.bound_root):
        raise Refusal("launcher_repository_mismatch")
    if args.binding_path:
        path = Path(os.path.abspath(args.binding_path))
        if path.is_symlink() or path != root / ".overseer/bin/ok":
            raise Refusal("launcher_location_mismatch")
    if bool(args.bound_root) != bool(args.bound_id) or bool(args.bound_root) != bool(args.binding_path):
        raise Refusal("launcher_binding_incomplete")
    if args.config:
        path = Path(args.config)
        if not path.is_absolute():
            path = root / path
        if path != root / CONFIG:
            raise Refusal("only_canonical_config_supported")
    return root


def branch(root):
    value = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", optional=True)
    if not value:
        raise Refusal("detached_head")
    return label(value)


def head(root):
    return git(root, "rev-parse", "--verify", "HEAD", optional=True) or "unborn"


def runtime():
    if (KIT / "VERSION").read_text().strip() != VERSION:
        raise Refusal("runtime_version_mismatch")
    data = b"".join(p.encode() + b"\0" + confined(KIT, p).read_bytes() + b"\0"
                    for p in runtime_files())
    return {"root": str(KIT), "version": VERSION, "sha256": digest(data)}


def config_for(root, args, *, syncing=False, authority=True):
    from cli.product_config import normalize
    data = read(root, CONFIG)
    normalized = normalize(data, root=root)
    config = normalized.data
    if not normalized.bound:
        raise Refusal("configuration_unbound: inspect with status; use init --migrate")
    repo = config["repo"]
    if repo["root"] != str(root):
        raise Refusal("config_repository_mismatch")
    if getattr(args, "bound_id", None) and repo["id"] != args.bound_id:
        raise Refusal("launcher_identity_mismatch")
    if config["runtime"]["root"] != str(KIT):
        raise Refusal("runtime_installation_mismatch")
    if not syncing and config["runtime"] != runtime():
        raise Refusal("runtime_changed: run this installation's explicit sync")
    if authority:
        revision(root, config)
    return config, data


def capture_context(root, config_data, config=None):
    from cli.product_config import normalize
    config = config or (normalize(config_data, root=root).data if config_data else None)
    if config is None or config['vcs']['canonical'] == 'git':
        if Path(git(root, 'rev-parse', '--show-toplevel')).resolve(strict=True) != root:
            raise Refusal('repository_context_changed')
        return {"config": config_data, "branch": branch(root), "head": head(root),
                "vcs": "git", "source_id": None}
    state = revision(root, config)
    return {"config": config_data, "branch": state.branch, "head": state.head,
            "vcs": state.kind, "source_id": state.source_id}


def check_context(root, config, args, captured):
    """Refuse a changed observation; never rebase a prepared prompt implicitly."""
    if root.resolve(strict=True) != root:
        raise Refusal("repository_context_changed")
    current, data = config_for(root, args)
    if current != config or data != captured["config"]:
        raise Refusal("config_context_changed")
    if capture_context(root, data, current) != captured:
        raise Refusal("repository_context_changed")


def check_expectations(meta, args):
    for field in ("repo_id", "branch", "lane", "model", "action_id", "action_kind"):
        expected = getattr(args, field, None)
        if expected is not None and meta[field] != expected:
            raise Refusal("expected_" + field + "_mismatch")


def parse_next(data):
    from cli.product_next import parse_collection
    collection = parse_collection(data)
    if collection is not None:
        return collection
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        raise Refusal("next_encoding_invalid") from None
    if not text.startswith("---\n") or "\r" in text:
        raise Refusal("next_frontmatter_invalid")
    parts = text[4:].split("\n---\n", 1)
    if len(parts) != 2:
        raise Refusal("next_frontmatter_invalid")
    meta = decode(parts[0].encode())
    prompt = parts[1]
    if not isinstance(meta, dict):
        raise Refusal("schema_keys_invalid")
    extra = ("vcs", "source_id") if meta.get("schema") == 2 else ()
    keys(meta, ("schema", "repo_id", "repo_root", "branch", "base_head", "lane",
                "model", "action_id", "action_kind", "prompt_sha256", *extra))
    if type(meta["schema"]) is not int or meta["schema"] not in (1, 2):
        raise Refusal("next_version_invalid")
    if extra and (meta["vcs"] not in ("git", "muse") or
                  (meta["vcs"] == "git" and meta["source_id"] is not None)):
        raise Refusal("next_revision_kind_invalid")
    for field in ("repo_id", "repo_root", "branch", "base_head", "model"):
        label(meta[field])
    token(meta["lane"])
    token(meta["action_id"])
    if meta["action_kind"] not in KINDS:
        raise Refusal("action_kind_invalid")
    validate_prompt(prompt)
    if meta["prompt_sha256"] != digest(prompt.encode()):
        raise Refusal("prompt_digest_mismatch")
    return meta, prompt


def validate_prompt(prompt):
    if not prompt.strip() or len(prompt.encode()) > 64000 or any(
        (ord(c) < 32 and c not in "\n\t") or ord(c) == 127 for c in prompt
    ):
        raise Refusal("prompt_invalid")
    # Binding lines are generated from metadata, never trusted from prose.
    if re.search(r"(?im)^\s*(repo(?:sitory)?(?: id| root)?|branch|lane|model|action id|action kind|step)\s*:", prompt):
        raise Refusal("prompt_contains_binding_fields")


def validate_next(root, config, data, args, *, context, freshness=True):
    from cli.product_next import selected_entry, selected_lane
    meta, prompt = parse_next(data)
    meta, prompt = selected_entry(meta, prompt, config, args)
    authority = config['vcs']['canonical']
    if meta.get("vcs", "git") != authority or meta.get('source_id') != context.get('source_id'):
        raise Refusal('next_authority_or_source_mismatch')
    for field, expected in {"repo_id": config["repo"]["id"], "repo_root": str(root),
                            "branch": context["branch"], 'lane': selected_lane(config, args)}.items():
        if meta[field] != expected:
            raise Refusal("next_" + field + "_mismatch")
    if len(config['docs']['lanes']) == 1 and meta['model'] != config['context']['model']:
        raise Refusal('next_model_mismatch')
    check_expectations(meta, args)
    if getattr(args, "expect_next", None) and args.expect_next != digest(data):
        raise Refusal("next_digest_mismatch")
    current = context["head"]
    if freshness and current != meta["base_head"]:
        if authority == 'muse':
            raise Refusal('next_stale_head')
        # Permit the one closing commit that publishes these exact NEXT bytes.
        # Any subsequent commit needs an explicit refresh through next-write.
        if current == "unborn":
            raise Refusal("next_stale_head")
        parents = git(root, "rev-list", "--parents", "-n", "1", current).split()[1:]
        expected_parents = [] if meta["base_head"] == "unborn" else [meta["base_head"]]
        committed = git(root, "show", current + ":" + NEXT, optional=True, raw=True)
        if parents != expected_parents or committed != data:
            raise Refusal("next_stale_head")
        if meta['schema'] == 3 and parents:
            previous = git(root, 'show', parents[0] + ':' + NEXT, optional=True, raw=True)
            if previous:
                old_meta, old_body = parse_next(previous)
                try:
                    old_meta, old_body = selected_entry(old_meta, old_body, config, args)
                except Refusal:
                    old_meta = {}
                if all(old_meta.get(k) == meta[k] for k in
                       ('branch', 'base_head', 'model', 'action_id', 'action_kind', 'prompt_sha256')):
                    raise Refusal('next_stale_head: lane not published by closing commit')
    return meta, prompt


def rendered(meta, prompt):
    binding = (f"Repository: {meta['repo_root']}\nRepository ID: {meta['repo_id']}\n"
               f"Branch: {meta['branch']}\nLane: {meta['lane']}\nModel: {meta['model']}\n"
               f"Action ID: {meta['action_id']}\nAction kind: {meta['action_kind']}\n")
    body = binding + "\n" + prompt.rstrip() + "\n"
    fence = "`" * max(3, 1 + max((len(x) for x in re.findall(r"`+", body)), default=0))
    return "## CURRENT NEXT — paste this\n\n" + fence + "text\n" + body + fence + "\n"


def write_next(root, config, args, prompt, *, expected, context):
    if getattr(args, 'batch_file', None):
        from cli.product_next import batch_publication
        payload = batch_publication(root, config, args, expected, context)
    else:
        from cli.product_next import selected_lane, publication
        lane = selected_lane(config, args)
        meta = {"schema": 1, "repo_id": config["repo"]["id"], "repo_root": str(root),
                "branch": context["branch"], "base_head": context["head"],
                'lane': lane, 'model': getattr(args, 'model', None) or config['context']['model'],
                "action_id": args.action_id, "action_kind": args.action_kind,
                "prompt_sha256": digest(prompt.encode())}
        if context.get('vcs') == 'muse':
            meta.update(schema=2, vcs='muse', source_id=context['source_id'])
            if getattr(args, 'vcs', None) != 'muse' or getattr(args, 'base_head', None) != context['head']:
                raise Refusal('muse_writer_requires_explicit_vcs_and_base_head')
        if getattr(args, 'vcs', None) not in (None, context.get('vcs', 'git')):
            raise Refusal('expected_vcs_mismatch')
        if getattr(args, 'base_head', None) not in (None, context['head']):
            raise Refusal('expected_base_head_mismatch')
        check_expectations(meta, args)
        payload = publication(root, config, meta, prompt, expected, reset=getattr(args, 'reset_authority', False))
        validate_next(root, config, payload, args, context=context, freshness=False)
    check_context(root, config, args, context)
    path = confined(root, NEXT, parents=True)
    # Advisory directory lock avoids ordinary concurrent lost updates without
    # persistent lock state or a recovery protocol.
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        check_context(root, config, args, context)
        atomic(root, NEXT, payload, expected=expected,
               before_replace=lambda: check_context(root, config, args, context))
    finally:
        os.close(fd)
    return payload


def launcher(root, identity, *, runtime_root=None):
    installation = KIT if runtime_root is None else Path(runtime_root)
    q = shlex.quote
    return ("#!/bin/sh\nset -eu\nPATH=/usr/bin:/bin\nexport PATH\n"
            "unset PYTHONPATH PYTHONHOME VIRTUAL_ENV\nexec "
            + q(str(installation / ".venv/bin/python3")) + " -I -B " + q(str(installation / "cli/bootstrap.py"))
            + " --bound-root " + q(str(root)) + " --bound-id " + q(identity)
            + ' --binding-path "$0" "$@"\n').encode()


def hook_script(root):
    from cli.product_bookends import hook_script as render_hook
    return render_hook(root)


def assets(root, config, hooks=False):
    result = {".overseer/bin/ok": launcher(root, config["repo"]["id"])}
    if hooks:
        from cli.product_bookends import cursor_assets, instruction_assets
        result.update(cursor_assets(root))
        result.update(instruction_assets(root))
    from cli.product_config import normalize
    from cli.footprint import resolve_footprint
    from cli.product_migration import _document_paths
    model = normalize(encode(config), root=root)
    living = _document_paths(config)
    for item in resolve_footprint(model.adapter, kit=KIT):
        if item.destination not in living and not item.destination.startswith('.cursor/hooks'):
            result[item.destination] = item.content
    result['policy/model-routing.yaml'] = (KIT / 'policy/model-routing.yaml').read_bytes()
    return result


def apply_assets(root, mapping, *, dry_run=False):
    updates = []
    # Validate all destinations before the first replacement.
    for path, data in mapping.items():
        target = confined(root, path, parents=not dry_run, missing_parents=dry_run)
        old = read(root, path, missing=True)
        mode = 0o755 if path.endswith(".sh") or path.endswith("/ok") else 0o644
        if old != data or (old is not None and stat.S_IMODE(target.stat().st_mode) != mode):
            updates.append((path, data, "absent" if old is None else digest(old), mode))
    if not dry_run:
        for path, data, expected, mode in updates:
            atomic(root, path, data, expected=expected, mode=mode)
    return [p for p, _, _, _ in updates]


def initialize(root, args):
    from cli.product_config import normalize
    from cli.product_migration import apply_mapping, classify_assets, _snapshot, _same, LAUNCHER, HOOKS
    from cli.product_authority import select, bind_muse, tracked_bindings
    from cli.v1_policy import ignore_assets
    existing = read(root, CONFIG, missing=True)
    if existing is not None:
        config, _ = config_for(root, args)
        if select(root, args, config) != config['vcs']['canonical'] or getattr(args, 'muse_python', None):
            raise Refusal('use_explicit_adopt_for_config_changes')
        for field, requested in (("lane", args.lane), ("model", args.model)):
            if requested is not None and config["context"][field] != requested:
                raise Refusal("init_context_change_requires_selection")
        if args.repo_name is not None and config["repo"]["name"] != args.repo_name:
            raise Refusal("init_repository_name_mismatch")
    else:
        bounded = {"schema": 1, "repo": {"name": label(args.repo_name or root.name),
                  "id": str(uuid.uuid4()), "root": str(root)}, "context": {
                  "lane": token(args.lane or "product"), "model": label(args.model or "GPT-6 Astra")},
                  "runtime": runtime(), "vcs": "git"}
        config = normalize(encode(bounded), root=root).data
        authority = select(root, args)
        if authority == 'muse':
            config = bind_muse(root, config, getattr(args, 'muse_python', None))
            config['vcs']['regime'] = args.regime or 'muse-only'
            if getattr(args, 'muse_staging_remote', None):
                config['vcs']['muse']['staging_remote'] = args.muse_staging_remote
            if getattr(args, 'mirror_branch', None):
                config['vcs']['git']['mirror_branch'] = args.mirror_branch
        elif getattr(args, 'muse_python', None):
            raise Refusal('git_does_not_use_muse_python')
    config = normalize(encode(config), root=root).data
    observed = capture_context(root, existing, config)
    config_data = encode(config) if existing is None else existing
    current = read(root, NEXT, missing=True)
    if current is not None:
        meta, _ = parse_next(current)
        present = meta["entries"] if meta["schema"] == 3 else (meta["lane"],)
        # Initialization validates existing entries without selecting a task or
        # creating missing lanes. NEXT retains its separate freshness/read policy.
        for lane in present:
            validate_next(root, config, current, argparse.Namespace(lane=lane),
                          context=observed, freshness=False)
    ignore_expected = {}
    mapping = assets(root, config, args.hooks)
    if existing is None and config['vcs']['canonical'] == 'muse':
        tracked = tracked_bindings(root, config)
        if any(tracked.values()) and getattr(args, 'tracked_bindings', None) != 'preserve':
            raise Refusal('tracked_local_bindings: explicitly choose --tracked-bindings preserve or untrack separately')
        mapping.update(ignore_assets(root, expected=ignore_expected))
    if existing is not None:
        for row in classify_assets(root, mapping, config):
            if row["classification"] == "preserved":
                mapping.pop(row["path"])
            elif row["classification"] in ("consumer-modified", "both-changed"):
                raise Refusal("init_asset_modified: " + row["path"])
    preserved = {}
    binding_assets = {LAUNCHER, *HOOKS, "scripts/muse-bridge-deploy.sh"}
    for path in list(mapping):
        confined(root, path, missing_parents=True)
        old = read(root, path, missing=True)
        if existing is None and old is not None and path not in ('.gitignore', '.museignore'):
            if path in binding_assets:
                raise Refusal("init_asset_exists: " + path)
            # Existing portable skills, rules, policies and references remain
            # consumer-owned. Operational bindings still require exact adoption.
            preserved[path] = _snapshot(root, path)
            mapping.pop(path)
    for path, body in {"docs/ROADMAP.md": "# Roadmap\n\nCurrent action: docs/NEXT.md.\n",
                       "docs/OVERSEER-HANDOVER.md": "# Handover\n\nRead current action with `ok next`.\n"}.items():
        confined(root, path, missing_parents=True)
        if read(root, path, missing=True) is None:
            mapping[path] = body.encode()
    from cli.product_footprint import with_lock
    mapping = with_lock(root, mapping, config, preserved=preserved)
    if existing is None:
        mapping[CONFIG] = config_data  # Binding is committed after all other assets.

    def recheck():
        for relative, snapshot in preserved.items():
            if not _same(root, snapshot):
                raise Refusal("init_preserved_asset_changed: " + relative)
        for relative, expected_digest in ignore_expected.items():
            body = read(root, relative, missing=True)
            if ('absent' if body is None else digest(body)) not in (expected_digest, digest(mapping[relative])):
                raise Refusal('stale_write: ' + relative)
        if (read(root, CONFIG, missing=True) != existing or runtime() != config["runtime"] or
                capture_context(root, existing, config) != observed):
            raise Refusal("init_context_changed")

    # All destinations are preflighted without mutation before creating the
    # directory used for the ordinary advisory lock on a fresh installation.
    for path in mapping:
        confined(root, path, missing_parents=True)
    if not args.dry_run:
        confined(root, CONFIG, parents=True)
    changed = apply_mapping(root, mapping, check_context=recheck, dry_run=args.dry_run)
    if not args.dry_run and existing is None and current is None:
        initial = argparse.Namespace(action_id="SETUP", action_kind="plan", bound_id=args.bound_id,
                                     vcs=observed['vcs'], base_head=observed['head'])
        write_next(root, config, initial, "Choose the first task for this repository.\n",
                   expected="absent", context=capture_context(root, config_data))
    return {"ok": True, "repository": config["repo"], "initialized": not args.dry_run,
            "dry_run": args.dry_run, "changed": changed}


def parser():
    """Compatibility import for tests; there is one product parser."""
    from cli.main import parser as product_parser
    return product_parser()


def main(argv=None):
    """Compatibility engine seam; always uses production context validation."""
    from cli.main import main as dispatch
    return dispatch(argv)


if __name__ == "__main__":
    print("refused: launch with cli/ok", file=sys.stderr)
    raise SystemExit(2)

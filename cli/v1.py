"""Repository-bound v1 commands. No registry, receipt, transaction, or network path."""
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
from cli.v1_policy import ignore_assets, local_path
from cli.v1_revision import discover, git, git_branch as branch, git_head as head, muse_read, revision

VERSION = "1.0.0"
KIT = Path(__file__).resolve().parent.parent
CONFIG = ".overseer/config.yaml"
NEXT = "docs/NEXT.md"
KINDS = ("plan", "implement", "review", "maintain", "stop")
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
RUNTIME_FILES = ("cli/__init__.py", "cli/bootstrap.py", "cli/main.py", "cli/ok",
                 "cli/overseer", "cli/v1.py", "cli/v1_io.py", "cli/v1_revision.py",
                 "cli/v1_muse_reader.py", "cli/v1_policy.py", "cli/digest.py", "VERSION")


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


def root_for(args) -> Path:
    cwd = Path.cwd().resolve()
    requested = Path(args.repo).expanduser().resolve(strict=True) if args.repo else cwd
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


def runtime():
    if (KIT / "VERSION").read_text().strip() != VERSION:
        raise Refusal("runtime_version_mismatch")
    data = b"".join(p.encode() + b"\0" + (KIT / p).read_bytes() + b"\0" for p in RUNTIME_FILES)
    return {"root": str(KIT), "version": VERSION, "sha256": digest(data)}


def config_for(root, args, *, syncing=False, data=None):
    data = read(root, CONFIG) if data is None else data
    config = decode(data)
    if not isinstance(config, dict):
        raise Refusal("schema_keys_invalid")
    muse = config.get("vcs") == "muse"
    keys(config, ("schema", "repo", "context", "runtime", "vcs", *(("muse",) if muse else ())))
    if (type(config["schema"]) is not int or config["schema"] not in (1, 2)
            or config["vcs"] not in ("git", "muse") or (muse and config["schema"] != 2)):
        raise Refusal("config_version_or_vcs_unsupported")
    if muse:
        keys(config["muse"], ("repo_id", "store", "runtime"))
        keys(config["muse"]["runtime"], ("python", "version", "sha256"))
        for value in (*config["muse"]["runtime"].values(), config["muse"]["repo_id"], config["muse"]["store"]):
            label(value)
    keys(config["repo"], ("name", "id", "root"))
    keys(config["context"], ("lane", "model"))
    keys(config["runtime"], ("root", "version", "sha256"))
    repo = config["repo"]
    label(repo["name"])
    try:
        if str(uuid.UUID(repo["id"])) != repo["id"]:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise Refusal("repo_identity_invalid") from None
    if repo["root"] != str(root):
        raise Refusal("config_repository_mismatch")
    if args.bound_id and repo["id"] != args.bound_id:
        raise Refusal("launcher_identity_mismatch")
    token(config["context"]["lane"])
    label(config["context"]["model"])
    if config["runtime"]["root"] != str(KIT):
        raise Refusal("runtime_installation_mismatch")
    if not syncing and config["runtime"] != runtime():
        raise Refusal("runtime_changed: run this installation's explicit sync")
    return config, data


def check_expectations(meta, args):
    for field in ("repo_id", "branch", "lane", "model", "action_id", "action_kind", "vcs", "base_head"):
        expected = getattr(args, field, None)
        actual = meta.get(field, "git" if field == "vcs" else None)
        if expected is not None and actual != expected:
            raise Refusal("expected_" + field + "_mismatch")


def parse_next(data):
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
    if re.search(r"(?im)^\s*(repo(?:sitory)?(?: id| root)?|branch|lane|model|action id|action kind|step|revision(?: kind)?|muse repository id)\s*:", prompt):
        raise Refusal("prompt_contains_binding_fields")


def validate_next(root, config, data, args, *, freshness=True, state=None):
    meta, prompt = parse_next(data)
    state = state or revision(root, config)
    if meta.get("vcs", "git") != state.kind or meta.get("source_id") != state.source_id:
        raise Refusal("next_revision_source_mismatch")
    for field, expected in {"repo_id": config["repo"]["id"], "repo_root": str(root),
                            "branch": state.branch, **config["context"]}.items():
        if meta[field] != expected:
            raise Refusal("next_" + field + "_mismatch")
    check_expectations(meta, args)
    if getattr(args, "expect_next", None) and args.expect_next != digest(data):
        raise Refusal("next_digest_mismatch")
    current = state.head
    if freshness and current != meta["base_head"]:
        if state.kind != "git":
            raise Refusal("next_stale_head")
        # Permit the one closing commit that publishes these exact NEXT bytes.
        # Any subsequent commit needs an explicit refresh through next-write.
        parents = git(root, "rev-list", "--parents", "-n", "1", "HEAD").split()[1:]
        expected_parents = [] if meta["base_head"] == "unborn" else [meta["base_head"]]
        committed = git(root, "show", "HEAD:" + NEXT, optional=True)
        if parents != expected_parents or committed != data.decode().strip():
            raise Refusal("next_stale_head")
    return meta, prompt


def rendered(meta, prompt):
    binding = (f"Repository: {meta['repo_root']}\nRepository ID: {meta['repo_id']}\n"
               f"Branch: {meta['branch']}\nLane: {meta['lane']}\nModel: {meta['model']}\n"
               f"Action ID: {meta['action_id']}\nAction kind: {meta['action_kind']}\n")
    if meta["schema"] == 2:
        binding += f"Revision kind: {meta['vcs']}\nRevision: {meta['base_head']}\n"
        if meta["vcs"] == "muse":
            binding += f"Muse repository ID: {meta['source_id']}\n"
    body = binding + "\n" + prompt.rstrip() + "\n"
    fence = "`" * max(3, 1 + max((len(x) for x in re.findall(r"`+", body)), default=0))
    return "## CURRENT NEXT — paste this\n\n" + fence + "text\n" + body + fence + "\n"


def write_next(root, config, args, prompt, *, expected):
    state = revision(root, config)
    if state.kind == "muse" and (getattr(args, "vcs", None) != "muse" or getattr(args, "base_head", None) is None):
        raise Refusal("muse_writer_requires_vcs_and_base_head")
    meta = {"schema": config["schema"], "repo_id": config["repo"]["id"], "repo_root": str(root),
            "branch": state.branch, "base_head": state.head, **config["context"],
            "action_id": args.action_id, "action_kind": args.action_kind,
            "prompt_sha256": digest(prompt.encode())}
    if meta["schema"] == 2:
        meta.update(vcs=state.kind, source_id=state.source_id)
    check_expectations(meta, args)
    payload = b"---\n" + encode(meta) + b"---\n" + prompt.encode()
    validate_next(root, config, payload, args, freshness=False, state=state)
    path = confined(root, NEXT, parents=True)
    # Advisory directory lock avoids ordinary concurrent lost updates without
    # persistent lock state or a recovery protocol.
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        if decode(read(root, CONFIG)) != config or revision(root, config) != state:
            raise Refusal("context_changed_before_write")
        atomic(root, NEXT, payload, expected=expected)
    finally:
        os.close(fd)
    return payload


def launcher(root, identity):
    q = shlex.quote
    return ("#!/bin/sh\nset -eu\nPATH=/usr/bin:/bin\nexport PATH\n"
            "unset PYTHONPATH PYTHONHOME VIRTUAL_ENV\nexec "
            + q(str(KIT / ".venv/bin/python3")) + " -I -B " + q(str(KIT / "cli/bootstrap.py"))
            + " --bound-root " + q(str(root)) + " --bound-id " + q(identity)
            + ' --binding-path "$0" "$@"\n').encode()


def hook_script(root):
    return ("#!/bin/sh\nset -eu\nexec " + shlex.quote(str(root / ".overseer/bin/ok"))
            + ' hook --hook-path "$0"\n').encode()


def assets(root, config, hooks=False):
    result = {".overseer/bin/ok": launcher(root, config["repo"]["id"])}
    if hooks:
        for name in ("session-start-next.sh", "session-end-closeout.sh"):
            result[".cursor/hooks/" + name] = hook_script(root)
        result[".cursor/hooks.json"] = (json.dumps({"version": 1, "hooks": {
            "sessionStart": [{"command": str(root / ".cursor/hooks/session-start-next.sh")}],
            "stop": [{"command": str(root / ".cursor/hooks/session-end-closeout.sh")}],
        }}, indent=2) + "\n").encode()
    return result


def apply_assets(root, mapping, *, dry_run=False, expected=None):
    updates = []
    # Validate all destinations before the first replacement.
    for path, data in mapping.items():
        target = confined(root, path, parents=not dry_run, missing_parents=dry_run)
        old = read(root, path, missing=True)
        prior = "absent" if old is None else digest(old)
        if expected is not None and path in expected and expected[path] != prior:
            raise Refusal("stale_write: " + path)
        mode = 0o755 if path.endswith(".sh") or path.endswith("/ok") else 0o644
        if old != data or (old is not None and stat.S_IMODE(target.stat().st_mode) != mode):
            updates.append((path, data, prior, mode))
    if not dry_run:
        for path, data, expected, mode in updates:
            atomic(root, path, data, expected=expected, mode=mode)
    return [p for p, _, _, _ in updates]


def selected_vcs(root, args, existing=None):
    selected = getattr(args, "vcs", None)
    regime = getattr(args, "regime", None)
    if regime:
        mapped = {"git-only": "git", "muse-only": "muse", "muse+git-mirror": "muse"}[regime]
        if selected and selected != mapped:
            raise Refusal("conflicting_vcs_selection")
        selected = mapped
    if selected is None:
        if existing:
            return existing["vcs"]
        if os.path.lexists(root / ".muse"):
            raise Refusal("explicit_vcs_selection_required")
        selected = "git"
    return selected


def bind_muse(root, config, python):
    if not python:
        raise Refusal("muse_python_required")
    state = muse_read(root, python)
    return dict(config, schema=2, vcs="muse", muse={
        "repo_id": state["repo_id"], "store": state["store"], "runtime": state["runtime"]})


def tracked_bindings(root, config):
    result = {}
    if os.path.lexists(root / ".git"):
        result["git"] = sorted(p for p in git(root, "ls-files", "-z").split("\0") if local_path(p))
    if config["vcs"] == "muse":
        result["muse"] = list(revision(root, config).tracked_local)
    # Git-only use deliberately does not inspect or load a Muse installation.
    return result


def adopt(root, config, original, args):
    if digest(original) != args.expect_config:
        raise Refusal("stale_write: " + CONFIG)
    for field, actual in {"repo_id": config["repo"]["id"], **config["context"]}.items():
        if getattr(args, field) != actual:
            raise Refusal("expected_" + field + "_mismatch")
    expected = {CONFIG: digest(original)}
    if args.restore_config:
        if args.muse_python:
            raise Refusal("rollback_uses_preserved_muse_binding")
        if not args.restore_config.startswith(".overseer/local/"):
            raise Refusal("rollback_requires_local_config_backup")
        payload = read(root, args.restore_config)
        updated, _ = config_for(root, args, syncing=True, data=payload)
        if updated["repo"] != config["repo"] or updated["context"] != config["context"]:
            raise Refusal("rollback_identity_or_context_mismatch")
        mapping = {}
    else:
        updated = dict(config, schema=2, vcs=args.vcs, runtime=runtime())
        updated.pop("muse", None)
        if args.vcs == "muse":
            python = args.muse_python or config.get("muse", {}).get("runtime", {}).get("python")
            updated = bind_muse(root, updated, python)
        elif args.muse_python:
            raise Refusal("git_does_not_use_muse_python")
        payload = encode(updated)
        mapping = ignore_assets(root, expected=expected)
    target = revision(root, updated)
    if target.branch != args.branch or target.head != args.base_head:
        raise Refusal("adoption_target_revision_mismatch")
    tracked = tracked_bindings(root, updated)
    backup = ".overseer/local/config-before-" + digest(original) + ".yaml"
    old_backup = read(root, backup, missing=True)
    if old_backup is not None and old_backup != original:
        raise Refusal("adoption_backup_mismatch")
    expected[backup] = "absent" if old_backup is None else digest(old_backup)
    mapping[backup] = original
    mapping[CONFIG] = payload
    changes = apply_assets(root, mapping, dry_run=True, expected=expected)
    result = {"ok": not any(tracked.values()), "repository": config["repo"],
              "vcs": updated["vcs"], "branch": target.branch, "head": target.head,
              "changed": changes, "backup": backup, "tracked_local": tracked,
              "config_sha256": digest(payload), "dry_run": args.dry_run,
              "next": "preserved; publish explicitly with next-write after authority change",
              "ignore_rollback": "additive exclusions retained; existing rules and edits preserved"}
    if not args.dry_run:
        if not result["ok"]:
            raise Refusal("tracked_local_bindings: review dry-run; no automatic untracking")
        if read(root, CONFIG) != original or revision(root, updated) != target:
            raise Refusal("context_changed_before_adoption")
        # Config is replaced last. A failure beforehand leaves the old binding
        # usable and additive ignores/backup safe to retain and retry.
        apply_assets(root, mapping, expected=expected)
    return result


def initialize(root, args):
    confined(root, CONFIG, parents=True)
    existing = read(root, CONFIG, missing=True)
    if existing is not None:
        config, _ = config_for(root, args)
        if selected_vcs(root, args, config) != config["vcs"] or args.muse_python:
            raise Refusal("use_explicit_adopt_for_config_changes")
    else:
        config = {"schema": 2, "repo": {"name": label(args.repo_name or root.name),
                  "id": str(uuid.uuid4()), "root": str(root)}, "context": {
                  "lane": token(args.lane), "model": label(args.model)},
                  "runtime": runtime(), "vcs": selected_vcs(root, args)}
        if config["vcs"] == "muse":
            config = bind_muse(root, config, args.muse_python)
        elif args.muse_python:
            raise Refusal("git_does_not_use_muse_python")
    state = revision(root, config)
    confined(root, NEXT, parents=True)
    current = read(root, NEXT, missing=True)
    if current is not None:
        validate_next(root, config, current, argparse.Namespace(), freshness=False)
    # Refuse preexisting unmanaged launchers rather than silently taking ownership.
    mapping = assets(root, config, args.hooks)
    ignores = ignore_assets(root)
    tracked = tracked_bindings(root, config)
    if existing is None and any(tracked.values()):
        raise Refusal("tracked_local_bindings: review and explicitly untrack before init")
    for path in ("docs/ROADMAP.md", "docs/OVERSEER-HANDOVER.md"):
        confined(root, path)
    for path in mapping:
        confined(root, path, parents=True)
        old = read(root, path, missing=True)
        if existing is None and old is not None:
            raise Refusal("init_asset_exists: " + path)
    if existing is None:
        atomic(root, CONFIG, encode(config), expected="absent")
    for path, body in {"docs/ROADMAP.md": "# Roadmap\n\nCurrent action: docs/NEXT.md.\n",
                       "docs/OVERSEER-HANDOVER.md": "# Handover\n\nRead current action with `ok next`.\n"}.items():
        if read(root, path, missing=True) is None:
            atomic(root, path, body.encode(), expected="absent")
    if current is None:
        initial = argparse.Namespace(action_id="SETUP", action_kind="plan", vcs=state.kind, base_head=state.head)
        write_next(root, config, initial, "Choose the first bounded task for this repository.\n", expected="absent")
    apply_assets(root, mapping)
    apply_assets(root, ignores)
    return {"ok": True, "repository": config["repo"], "initialized": True}


def parser():
    p = argparse.ArgumentParser(prog="ok", description="Bounded repository and NEXT utility",
                                allow_abbrev=False)
    def globals_to(target):
        for names, opts in [(("-C", "--repo"), {}), (("--config",), {}),
                            (("--json",), {"action": "store_true"}),
                            (("--bound-root",), {"help": argparse.SUPPRESS}),
                            (("--bound-id",), {"help": argparse.SUPPRESS}),
                            (("--binding-path",), {"help": argparse.SUPPRESS})]:
            target.add_argument(*names, default=argparse.SUPPRESS, **opts)
    globals_to(p)
    p.set_defaults(repo=None, config=None, json=False, bound_root=None, bound_id=None, binding_path=None)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("status", "init", "sync", "adopt", "next", "next-write", "hook"):
        cmd = sub.add_parser(name, allow_abbrev=False)
        globals_to(cmd)
        if name == "init":
            cmd.add_argument("--regime", choices=("git-only", "muse-only", "muse+git-mirror"))
            cmd.add_argument("--vcs", choices=("git", "muse"))
            cmd.add_argument("--muse-python", help="Absolute Python path in the separate Muse venv")
            cmd.add_argument("--repo-name")
            cmd.add_argument("--lane", default="product")
            cmd.add_argument("--model", default="GPT-6 Astra")
            cmd.add_argument("--non-interactive", action="store_true")
        if name in ("init", "sync"):
            cmd.add_argument("--hooks", action="store_true", help="Install bound hooks (fixtures only in this milestone)")
        if name == "sync":
            cmd.add_argument("--dry-run", action="store_true")
        if name == "adopt":
            selection = cmd.add_mutually_exclusive_group(required=True)
            selection.add_argument("--vcs", choices=("git", "muse"))
            selection.add_argument("--restore-config", help="Confined .overseer/local config backup")
            cmd.add_argument("--muse-python")
            cmd.add_argument("--expect-config", required=True)
            for field in ("repo-id", "branch", "lane", "model", "base-head"):
                cmd.add_argument("--" + field, required=True)
            cmd.add_argument("--dry-run", action="store_true")
        if name in ("next", "next-write", "status"):
            for field in ("repo-id", "branch", "lane", "model", "action-id", "action-kind"):
                cmd.add_argument("--" + field, required=name == "next-write",
                                 choices=KINDS if field == "action-kind" else None)
            cmd.add_argument("--expect-next", required=name == "next-write")
            cmd.add_argument("--vcs", choices=("git", "muse"))
            cmd.add_argument("--base-head", help="Expected authoritative revision; required for Muse writes")
        if name == "next-write":
            cmd.add_argument("--prompt-file", required=True, help="Confined repository-relative UTF-8 file")
        if name == "hook":
            cmd.add_argument("--hook-path", required=True)
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    lock = None
    try:
        # Argparse's last-wins behavior must not override a bound launcher's root.
        for aliases in (("-C", "--repo"), ("--config",), ("--bound-root",), ("--bound-id",), ("--binding-path",)):
            if sum(a.split("=", 1)[0] in aliases or (a.startswith("-C") and a != "-C" and "-C" in aliases) for a in argv) > 1:
                raise Refusal("duplicate_binding_option")
        args = parser().parse_args(argv)
        root = root_for(args)
        if args.command in ("init", "sync", "adopt", "next-write"):
            lock = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            fcntl.flock(lock, fcntl.LOCK_EX)
        if args.command == "init":
            result = initialize(root, args)
        else:
            config, original = config_for(root, args, syncing=args.command in ("sync", "adopt"))
            if args.command == "adopt":
                result = adopt(root, config, original, args)
            elif args.command == "sync":
                confined(root, NEXT)
                revision(root, config)
                updated = dict(config, runtime=runtime())
                mapping = assets(root, updated, args.hooks)
                mapping[CONFIG] = encode(updated)
                changed = apply_assets(root, mapping, dry_run=args.dry_run)
                result = {"ok": True, "repository": config["repo"], "changed": changed, "dry_run": args.dry_run}
            elif args.command == "next-write":
                prompt = read(root, args.prompt_file).decode("utf-8")
                if not prompt.endswith("\n"):
                    prompt += "\n"
                # The expected digest applies to the old NEXT, not the new candidate.
                expected = args.expect_next
                args.expect_next = None
                result = {"ok": True, "next_sha256": digest(write_next(root, config, args, prompt, expected=expected))}
            else:
                if args.command == "hook":
                    path = Path(os.path.abspath(args.hook_path))
                    if not args.bound_id or path.is_symlink() or path not in (
                        root / ".cursor/hooks/session-start-next.sh", root / ".cursor/hooks/session-end-closeout.sh"):
                        raise Refusal("hook_location_mismatch")
                    if not sys.stdin.isatty():
                        raw = sys.stdin.buffer.read(LIMIT + 1)
                        if len(raw) > LIMIT:
                            raise Refusal("hook_input_too_large")
                        if raw.strip():
                            event = json.loads(raw)
                            if not isinstance(event, dict):
                                raise Refusal("hook_input_invalid")
                            roots = event.get("workspace_roots", [])
                            if roots and (not isinstance(roots, list) or len(roots) != 1 or not isinstance(roots[0], str) or Path(roots[0]).resolve() != root):
                                raise Refusal("hook_workspace_mismatch")
                state = revision(root, config, dirty=args.command == "status")
                result = {"ok": True, "repository": config["repo"], "branch": state.branch,
                          "head": state.head, "vcs": state.kind, "source_id": state.source_id,
                          "runtime": runtime(), "config_sha256": digest(original),
                          "publication": "not_checked_offline"}
                try:
                    data = read(root, NEXT)
                    meta, prompt = validate_next(root, config, data, args, state=state)
                    result.update(next=meta, next_sha256=digest(data))
                except Refusal as exc:
                    if args.command != "status":
                        raise
                    result.update(ok=False, next_error=str(exc))
                if args.command in ("next", "hook"):
                    output = rendered(meta, prompt)
                    if args.command == "hook":
                        print(json.dumps({"additional_context": output, "followup_message": output}))
                    elif args.json:
                        print(json.dumps(dict(result, prompt=prompt, rendered=output)))
                    else:
                        print(output, end="")
                    return 0
                result["dirty"] = state.dirty
                if state.kind == "muse":
                    result["dirty_basis"] = "working_files_vs_snapshot_and_shared_stage"
                    result["tracked_local"] = list(state.tracked_local)
        if args.json:
            print(json.dumps(result))
        else:
            print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    except (Refusal, OSError, ValueError, UnicodeError, subprocess.SubprocessError) as exc:
        # No partial prompt and no traceback/config bytes on refusal.
        message = str(exc) if isinstance(exc, Refusal) else type(exc).__name__
        print("refused: " + message[:300], file=sys.stderr)
        return 2
    finally:
        if lock is not None:
            os.close(lock)


if __name__ == "__main__":
    raise SystemExit(main())

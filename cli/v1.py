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

VERSION = "1.0.0"
KIT = Path(__file__).resolve().parent.parent
CONFIG = ".overseer/config.yaml"
NEXT = "docs/NEXT.md"
KINDS = ("plan", "implement", "review", "maintain", "stop")
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
RUNTIME_FILES = ("cli/__init__.py", "cli/bootstrap.py", "cli/main.py", "cli/ok",
                 "cli/overseer", "cli/v1.py", "cli/v1_io.py", "cli/digest.py", "VERSION")


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


def git(root: Path, *args: str, optional: bool = False) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(PATH="/usr/bin:/bin", GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL="/dev/null", LC_ALL="C")
    proc = subprocess.run(["/usr/bin/git", "-c", "core.fsmonitor=false", "-c",
                           "core.hooksPath=/dev/null", "-C", str(root), *args],
                          env=env, capture_output=True, text=True, timeout=15)
    if proc.returncode and not optional:
        raise Refusal("git_read_failed: " + args[0])
    return proc.stdout.strip() if proc.returncode == 0 else ""


def root_for(args) -> Path:
    cwd = Path.cwd().resolve()
    requested = Path(args.repo).expanduser().resolve(strict=True) if args.repo else cwd
    top = git(requested, "rev-parse", "--show-toplevel")
    root = Path(top).resolve(strict=True)
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
    data = b"".join(p.encode() + b"\0" + (KIT / p).read_bytes() + b"\0" for p in RUNTIME_FILES)
    return {"root": str(KIT), "version": VERSION, "sha256": digest(data)}


def config_for(root, args, *, syncing=False):
    data = read(root, CONFIG)
    config = decode(data)
    keys(config, ("schema", "repo", "context", "runtime", "vcs"))
    if type(config["schema"]) is not int or config["schema"] != 1 or config["vcs"] != "git":
        raise Refusal("config_version_or_vcs_unsupported")
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
    for field in ("repo_id", "branch", "lane", "model", "action_id", "action_kind"):
        expected = getattr(args, field, None)
        if expected is not None and meta[field] != expected:
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
    keys(meta, ("schema", "repo_id", "repo_root", "branch", "base_head", "lane",
                "model", "action_id", "action_kind", "prompt_sha256"))
    if type(meta["schema"]) is not int or meta["schema"] != 1:
        raise Refusal("next_version_invalid")
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


def validate_next(root, config, data, args, *, freshness=True):
    meta, prompt = parse_next(data)
    for field, expected in {"repo_id": config["repo"]["id"], "repo_root": str(root),
                            "branch": branch(root), **config["context"]}.items():
        if meta[field] != expected:
            raise Refusal("next_" + field + "_mismatch")
    check_expectations(meta, args)
    if getattr(args, "expect_next", None) and args.expect_next != digest(data):
        raise Refusal("next_digest_mismatch")
    current = head(root)
    if freshness and current != meta["base_head"]:
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
    body = binding + "\n" + prompt.rstrip() + "\n"
    fence = "`" * max(3, 1 + max((len(x) for x in re.findall(r"`+", body)), default=0))
    return "## CURRENT NEXT — paste this\n\n" + fence + "text\n" + body + fence + "\n"


def write_next(root, config, args, prompt, *, expected):
    meta = {"schema": 1, "repo_id": config["repo"]["id"], "repo_root": str(root),
            "branch": branch(root), "base_head": head(root), **config["context"],
            "action_id": args.action_id, "action_kind": args.action_kind,
            "prompt_sha256": digest(prompt.encode())}
    check_expectations(meta, args)
    payload = b"---\n" + encode(meta) + b"---\n" + prompt.encode()
    validate_next(root, config, payload, args, freshness=False)
    path = confined(root, NEXT, parents=True)
    # Advisory directory lock avoids ordinary concurrent lost updates without
    # persistent lock state or a recovery protocol.
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
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
    if args.regime != "git-only":
        raise Refusal("v1_requires_git_checkout")
    confined(root, CONFIG, parents=True)
    existing = read(root, CONFIG, missing=True)
    if existing is not None:
        config, _ = config_for(root, args)
    else:
        config = {"schema": 1, "repo": {"name": label(args.repo_name or root.name),
                  "id": str(uuid.uuid4()), "root": str(root)}, "context": {
                  "lane": token(args.lane), "model": label(args.model)},
                  "runtime": runtime(), "vcs": "git"}
    confined(root, NEXT, parents=True)
    current = read(root, NEXT, missing=True)
    if current is not None:
        validate_next(root, config, current, argparse.Namespace(), freshness=False)
    # Refuse preexisting unmanaged launchers rather than silently taking ownership.
    mapping = assets(root, config, args.hooks)
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
        initial = argparse.Namespace(action_id="SETUP", action_kind="plan")
        write_next(root, config, initial, "Choose the first bounded task for this repository.\n", expected="absent")
    apply_assets(root, mapping)
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
    for name in ("status", "init", "sync", "next", "next-write", "hook"):
        cmd = sub.add_parser(name, allow_abbrev=False)
        globals_to(cmd)
        if name == "init":
            cmd.add_argument("--regime", default="git-only")
            cmd.add_argument("--repo-name")
            cmd.add_argument("--lane", default="product")
            cmd.add_argument("--model", default="GPT-6 Astra")
            cmd.add_argument("--non-interactive", action="store_true")
        if name in ("init", "sync"):
            cmd.add_argument("--hooks", action="store_true", help="Install bound hooks (fixtures only in this milestone)")
        if name == "sync":
            cmd.add_argument("--dry-run", action="store_true")
        if name in ("next", "next-write", "status"):
            for field in ("repo-id", "branch", "lane", "model", "action-id", "action-kind"):
                cmd.add_argument("--" + field, required=name == "next-write",
                                 choices=KINDS if field == "action-kind" else None)
            cmd.add_argument("--expect-next", required=name == "next-write")
        if name == "next-write":
            cmd.add_argument("--prompt-file", required=True, help="Confined repository-relative UTF-8 file")
        if name == "hook":
            cmd.add_argument("--hook-path", required=True)
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        # Argparse's last-wins behavior must not override a bound launcher's root.
        for aliases in (("-C", "--repo"), ("--config",), ("--bound-root",), ("--bound-id",), ("--binding-path",)):
            if sum(a.split("=", 1)[0] in aliases or (a.startswith("-C") and a != "-C" and "-C" in aliases) for a in argv) > 1:
                raise Refusal("duplicate_binding_option")
        args = parser().parse_args(argv)
        root = root_for(args)
        if args.command == "init":
            result = initialize(root, args)
        else:
            config, original = config_for(root, args, syncing=args.command == "sync")
            if args.command == "sync":
                confined(root, NEXT)
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
                result = {"ok": True, "repository": config["repo"], "branch": branch(root), "head": head(root), "runtime": runtime()}
                try:
                    data = read(root, NEXT)
                    meta, prompt = validate_next(root, config, data, args)
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
                result["dirty"] = bool(git(root, "status", "--porcelain", "--untracked-files=normal"))
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


if __name__ == "__main__":
    raise SystemExit(main())

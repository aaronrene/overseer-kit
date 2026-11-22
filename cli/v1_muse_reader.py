"""Read-only bridge to exactly reviewed Muse releases in a separate venv.

Do not call the native CLI: require_repo performs GC and some stage readers
migrate files. Only object reads, ignore matching and hashing are reused here.
Linked worktree HEAD is resolved explicitly; native CLI discovery returns the
main store root. This reader never writes refs, caches, hooks or application files.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import stat
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cli.v1_io import Refusal, read
from cli.v1_policy import local_path
from cli.v1_revision import MUSE_RUNTIMES, OID, unique_json


def readonly(event, args):
    # A compatibility assertion for pinned Python APIs, not a hostile-code
    # sandbox. Refuse unexpected writes/network/child processes on this path.
    if event == "open" and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
        raise Refusal("muse_reader_write_attempt")
    if event in {"os.remove", "os.rename", "os.rmdir", "os.mkdir", "os.chmod",
                 "os.link", "os.symlink", "os.truncate", "subprocess.Popen",
                 "os.system", "socket.connect", "socket.bind"}:
        raise Refusal("muse_reader_side_effect")


def document(root, path):
    return json.loads(read(root, path), object_pairs_hook=unique_json)


def layout(root, version, observe=read):
    marker = root / ".muse"
    if marker.is_symlink():
        raise Refusal("muse_marker_symlink")
    if marker.is_dir():
        return root, ".muse/HEAD", None, ".muse"
    pointer = observe(root, ".muse").decode().strip()
    if not pointer.startswith("musestore: "):
        raise Refusal("muse_pointer_invalid")
    path = Path(pointer[len("musestore: "):])
    if not path.is_absolute() or path.name != ".muse" or path.resolve() != path or not path.is_dir():
        raise Refusal("muse_pointer_invalid")
    store = path.parent
    matches = []
    for entry in (path / "worktrees").glob("*.json"):
        data = json.loads(observe(store, str(entry.relative_to(store))), object_pairs_hook=unique_json)
        if data.get("path") == str(root):
            name = data.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or entry.stem != name:
                raise Refusal("muse_worktree_invalid")
            state = ".muse/worktrees/" + name if version == "0.2.3rc8" else ".muse"
            head = state + "/HEAD" if version == "0.2.3rc8" else ".muse/worktrees/" + name + ".HEAD"
            if version == "0.2.3rc8" and observe(store, head, missing=True) is None:
                raise Refusal("muse_worktree_repair_required")
            matches.append((head, data.get("branch"), state))
    if len(matches) != 1:
        raise Refusal("muse_worktree_unregistered")
    return store, *matches[0]


def run(root, with_dirty):
    sys.addaudithook(readonly)
    version = importlib.metadata.version("muse")
    if sys.prefix == sys.base_prefix or version not in MUSE_RUNTIMES:
        raise Refusal("muse_version_unsupported")
    import muse
    package = Path(muse.__file__).resolve().parent
    if not package.is_relative_to(Path(sys.prefix).resolve()):
        raise Refusal("muse_import_origin_mismatch")
    source_hash = hashlib.sha256()
    for path in sorted(package.rglob("*.py")):
        source_hash.update(str(path.relative_to(package)).encode() + b"\0" + path.read_bytes() + b"\0")
    if source_hash.hexdigest() != MUSE_RUNTIMES[version]:
        raise Refusal("muse_source_digest_unsupported")
    from muse.core.commits import read_commit
    from muse.core.snapshots import read_snapshot
    from muse.core.validation import validate_branch_name

    observed = {}

    def observe(base, path, *, missing=False):
        value = read(base, path, missing=missing)
        key = (base, path)
        if key in observed and observed[key] != value:
            raise Refusal("muse_revision_changed_during_read")
        observed[key] = value
        return value

    store, head_path, registered_branch, state_dir = layout(root, version, observe)
    identity = json.loads(observe(store, ".muse/repo.json"), object_pairs_hook=unique_json)
    if identity.get("domain") != "code" or not OID.fullmatch(identity.get("repo_id", "")):
        raise Refusal("muse_identity_or_domain_unsupported")
    head_data = observe(store, head_path)
    symbolic = head_data.decode().strip()
    prefix = "ref: refs/heads/" if registered_branch is None or version == "0.2.3rc8" else "refs/heads/"
    if not symbolic.startswith(prefix):
        raise Refusal("muse_detached_or_malformed_head")
    branch = symbolic[len(prefix):]
    validate_branch_name(branch)
    if registered_branch is not None and registered_branch != branch:
        raise Refusal("muse_worktree_branch_mismatch")
    ref_path = ".muse/refs/heads/" + branch
    ref = observe(store, ref_path, missing=True)
    head = "unborn" if ref in (None, b"") else ref.decode().strip()
    if head != "unborn" and not OID.fullmatch(head):
        raise Refusal("muse_ref_invalid")
    for name in ("CHECKOUT_HEAD", "MERGE_STATE.json"):
        if observe(store, state_dir + "/" + name, missing=True) is not None:
            raise Refusal("muse_checkout_or_merge_in_progress")
    manifest = {}
    directories = []
    if head != "unborn":
        commit = read_commit(store, head)
        snapshot = read_snapshot(store, commit.snapshot_id) if commit else None
        if snapshot is None:
            raise Refusal("muse_revision_objects_missing_or_corrupt")
        manifest = snapshot.manifest
        directories = snapshot.directories
    for path, oid in manifest.items():
        if Path(path).is_absolute() or ".." in Path(path).parts or not OID.fullmatch(oid):
            raise Refusal("muse_manifest_invalid")
    # Never call read_stage: its legacy-format path deletes the old index.
    stage_raw = observe(store, state_dir + "/code/stage.json", missing=True)
    stage = json.loads(stage_raw, object_pairs_hook=unique_json) if stage_raw else {"entries": {}}
    if not isinstance(stage, dict) or not isinstance(stage.get("entries"), dict):
        raise Refusal("muse_stage_invalid")
    tracked = sorted(p for p in set(manifest) | set(stage["entries"]) if local_path(p))
    dirty = None
    if with_dirty:
        from muse.core.ignore import is_ignored, resolve_patterns
        from muse.core.types import hash_file

        raw_ignore = observe(root, ".museignore", missing=True)
        if version == "0.2.3rc8":
            # Reuse the pure policy, never the native walker/stat cache (writes).
            from muse.core.exclusion import ALWAYS_PRUNE_DIRS, load_exclusion_policy
            policy = load_exclusion_policy(root, "code")
            ignored = lambda path: policy.decide(path).excluded
            prune = policy.prunes_dir
            ignored_dirs = ALWAYS_PRUNE_DIRS
        else:
            from muse.core.snapshot import _BUILTIN_SECRET_PATTERNS
            from muse.plugins.code.plugin import _ALWAYS_IGNORE_DIRS
            ignore = tomllib.loads(raw_ignore.decode()) if raw_ignore else {}
            patterns = _BUILTIN_SECRET_PATTERNS + resolve_patterns(ignore, "code")
            ignored = lambda path: is_ignored(path, patterns)
            prune = lambda path: is_ignored(path + "/_", patterns)
            ignored_dirs = _ALWAYS_IGNORE_DIRS
        current = {}
        for directory, dirs, files in os.walk(root, followlinks=False):
            here = Path(directory)
            rel = here.relative_to(root)
            dirs[:] = [d for d in dirs if d not in ignored_dirs
                       and not (here / d).is_symlink() and not (here / d / ".muse").exists()
                       and not prune((rel / d).as_posix())]
            for name in files:
                if name in (".muse", ".git"):
                    continue
                path = here / name
                relative = path.relative_to(root).as_posix()
                if ignored(relative):
                    continue
                if stat.S_ISREG(path.lstat().st_mode):
                    current[relative] = hash_file(path)
        # Older releases share stage; rc8 uses each checkout's own stage.
        dirty = bool(stage["entries"]) or current != manifest or any(
            not (root / d).is_dir() for d in directories)
    if any(read(base, path, missing=True) != value
           for (base, path), value in observed.items()):
        raise Refusal("muse_revision_changed_during_read")
    return {"root": str(root), "store": str(store), "repo_id": identity["repo_id"],
            "branch": branch, "head": head, "dirty": dirty, "tracked_local": tracked,
            "runtime": {"python": str(Path(sys.prefix).resolve() / "bin" / Path(sys.executable).name),
                        "version": version, "sha256": source_hash.hexdigest()}}


if __name__ == "__main__":
    try:
        print(json.dumps(run(Path(sys.argv[1]), sys.argv[2] == "dirty")))
    except Exception as exc:
        print("muse reader refused: " + (str(exc) if isinstance(exc, Refusal) else type(exc).__name__), file=sys.stderr)
        raise SystemExit(2)

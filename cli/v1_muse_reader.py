"""Read-only bridge to Muse 0.2.1rc5, executed in its own conventional venv.

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
from cli.v1_revision import MUSE_VERSION, OID, unique_json


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


def layout(root):
    marker = root / ".muse"
    if marker.is_symlink():
        raise Refusal("muse_marker_symlink")
    if marker.is_dir():
        return root, ".muse/HEAD", None
    pointer = read(root, ".muse").decode().strip()
    if not pointer.startswith("musestore: "):
        raise Refusal("muse_pointer_invalid")
    path = Path(pointer[len("musestore: "):])
    if not path.is_absolute() or path.name != ".muse" or path.resolve() != path or not path.is_dir():
        raise Refusal("muse_pointer_invalid")
    store = path.parent
    matches = []
    for entry in (path / "worktrees").glob("*.json"):
        data = document(store, str(entry.relative_to(store)))
        if data.get("path") == str(root):
            name = data.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or entry.stem != name:
                raise Refusal("muse_worktree_invalid")
            matches.append((".muse/worktrees/" + name + ".HEAD", data.get("branch")))
    if len(matches) != 1:
        raise Refusal("muse_worktree_unregistered")
    return store, *matches[0]


def run(root, with_dirty):
    sys.addaudithook(readonly)
    if sys.prefix == sys.base_prefix or importlib.metadata.version("muse") != MUSE_VERSION:
        raise Refusal("muse_version_unsupported")
    import muse
    package = Path(muse.__file__).resolve().parent
    if not package.is_relative_to(Path(sys.prefix).resolve()):
        raise Refusal("muse_import_origin_mismatch")
    source_hash = hashlib.sha256()
    for path in sorted(package.rglob("*.py")):
        source_hash.update(str(path.relative_to(package)).encode() + b"\0" + path.read_bytes() + b"\0")
    from muse.core.commits import read_commit
    from muse.core.snapshots import read_snapshot
    from muse.core.validation import validate_branch_name

    store, head_path, registered_branch = layout(root)
    identity = document(store, ".muse/repo.json")
    if identity.get("domain") != "code" or not OID.fullmatch(identity.get("repo_id", "")):
        raise Refusal("muse_identity_or_domain_unsupported")
    head_data = read(store, head_path)
    symbolic = head_data.decode().strip()
    prefix = "ref: refs/heads/" if registered_branch is None else "refs/heads/"
    if not symbolic.startswith(prefix):
        raise Refusal("muse_detached_or_malformed_head")
    branch = symbolic[len(prefix):]
    validate_branch_name(branch)
    if registered_branch is not None and registered_branch != branch:
        raise Refusal("muse_worktree_branch_mismatch")
    ref_path = ".muse/refs/heads/" + branch
    ref = read(store, ref_path, missing=True)
    head = "unborn" if ref in (None, b"") else ref.decode().strip()
    if head != "unborn" and not OID.fullmatch(head):
        raise Refusal("muse_ref_invalid")
    for name in ("CHECKOUT_HEAD", "MERGE_STATE.json"):
        if (store / ".muse" / name).exists():
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
    stage_raw = read(store, ".muse/code/stage.json", missing=True)
    stage = json.loads(stage_raw, object_pairs_hook=unique_json) if stage_raw else {"entries": {}}
    if not isinstance(stage, dict) or not isinstance(stage.get("entries"), dict):
        raise Refusal("muse_stage_invalid")
    tracked = sorted(p for p in set(manifest) | set(stage["entries"]) if local_path(p))
    dirty = None
    if with_dirty:
        from muse.core.ignore import is_ignored, resolve_patterns
        from muse.core.snapshot import _BUILTIN_SECRET_PATTERNS
        from muse.core.types import hash_file
        from muse.plugins.code.plugin import _ALWAYS_IGNORE_DIRS

        raw_ignore = read(root, ".museignore", missing=True)
        ignore = tomllib.loads(raw_ignore.decode()) if raw_ignore else {}
        patterns = _BUILTIN_SECRET_PATTERNS + resolve_patterns(ignore, "code")
        current = {}
        for directory, dirs, files in os.walk(root, followlinks=False):
            here = Path(directory)
            rel = here.relative_to(root)
            dirs[:] = [d for d in dirs if d not in _ALWAYS_IGNORE_DIRS
                       and not (here / d).is_symlink() and not (here / d / ".muse").exists()
                       and not is_ignored((rel / d / "_").as_posix(), patterns)]
            for name in files:
                if name in (".muse", ".git"):
                    continue
                path = here / name
                relative = path.relative_to(root).as_posix()
                if is_ignored(relative, patterns):
                    continue
                if stat.S_ISREG(path.lstat().st_mode):
                    current[relative] = hash_file(path)
        # Staging is shared by this Muse version. It is reported dirty in any
        # linked checkout too; do not mistake the primary index for a clean lane.
        dirty = bool(stage["entries"]) or current != manifest or any(
            not (root / d).is_dir() for d in directories)
    if read(store, head_path) != head_data or read(store, ref_path, missing=True) != ref:
        raise Refusal("muse_revision_changed_during_read")
    return {"root": str(root), "store": str(store), "repo_id": identity["repo_id"],
            "branch": branch, "head": head, "dirty": dirty, "tracked_local": tracked,
            "runtime": {"python": str(Path(sys.prefix).resolve() / "bin" / Path(sys.executable).name),
                        "version": MUSE_VERSION, "sha256": source_hash.hexdigest()}}


if __name__ == "__main__":
    try:
        print(json.dumps(run(Path(sys.argv[1]), sys.argv[2] == "dirty")))
    except Exception as exc:
        print("muse reader refused: " + (str(exc) if isinstance(exc, Refusal) else type(exc).__name__), file=sys.stderr)
        raise SystemExit(2)

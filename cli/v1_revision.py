"""Explicit local revision selection. Git never imports or launches Muse."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import time

from cli.v1_io import Refusal

MUSE_VERSION = "0.2.1rc5"
OID = re.compile(r"sha256:[0-9a-f]{64}\Z")
RESPONSE_LIMIT = 2 * 1024 * 1024


def bounded_run(argv, *, cwd, env, timeout=15, limit=RESPONSE_LIMIT):
    """Bound elapsed time and combined output before accumulating a response."""
    with subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as proc:
        output = bytearray()
        count = 0
        deadline = time.monotonic() + timeout
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(proc.stdout, selectors.EVENT_READ)
                selector.register(proc.stderr, selectors.EVENT_READ)
                while selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise Refusal("muse_read_timeout")
                    for key, _ in selector.select(remaining):
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        count += len(chunk)
                        if count > limit:
                            raise Refusal("muse_response_too_large")
                        if key.fileobj is proc.stdout:
                            output.extend(chunk)
            proc.wait(timeout=max(0.01, deadline - time.monotonic()))
            return subprocess.CompletedProcess(argv, proc.returncode, bytes(output), b"")
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()


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


def discover(requested: Path) -> Path:
    for root in (requested, *requested.parents):
        # Stop at the nearest VCS boundary, including invalid markers. Do not
        # fall through a Muse checkout to an unrelated parent Git repository.
        if any(os.path.lexists(root / p) for p in (".git", ".muse")):
            return root
    raise Refusal("repository_not_found")


def git_branch(root):
    value = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", optional=True)
    if not value:
        raise Refusal("detached_head")
    return value


def git_head(root):
    return git(root, "rev-parse", "--verify", "HEAD", optional=True) or "unborn"


def unique_json(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refusal("muse_response_duplicate_key")
        result[key] = value
    return result


def muse_read(root, python, *, dirty=False):
    executable = Path(python)
    if not executable.is_absolute() or executable.parent.name != "bin":
        raise Refusal("muse_python_requires_absolute_venv_path")
    # Preserve the conventional venv Python symlink; resolving it would select
    # the base interpreter and lose the separate Muse installation.
    executable = executable.parent.resolve() / executable.name
    if not (executable.parent.parent / "pyvenv.cfg").is_file():
        raise Refusal("muse_python_requires_separate_venv")
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("GIT_", "MUSE_", "PYTHON")) and k != "VIRTUAL_ENV"}
    env.update(PATH="/usr/bin:/bin", PYTHONDONTWRITEBYTECODE="1", LC_ALL="C")
    reader = Path(__file__).with_name("v1_muse_reader.py")
    proc = bounded_run([str(executable), "-I", "-B", str(reader), str(root),
                        "dirty" if dirty else "revision"], cwd=root, env=env)
    if proc.returncode or len(proc.stdout) > RESPONSE_LIMIT:
        raise Refusal("muse_read_failed")
    try:
        value = json.loads(proc.stdout, object_pairs_hook=unique_json)
        required = {"root", "store", "repo_id", "branch", "head", "dirty",
                    "tracked_local", "runtime"}
        if not isinstance(value, dict) or set(value) != required:
            raise ValueError()
        runtime = value["runtime"]
        if (not isinstance(runtime, dict) or set(runtime) != {"python", "version", "sha256"}
                or runtime["python"] != str(executable) or runtime["version"] != MUSE_VERSION
                or not re.fullmatch(r"[0-9a-f]{64}", runtime["sha256"])):
            raise ValueError()
        if value["root"] != str(root) or not Path(value["store"]).is_absolute():
            raise ValueError()
        if not OID.fullmatch(value["repo_id"]):
            raise ValueError()
        if value["head"] != "unborn" and not OID.fullmatch(value["head"]):
            raise ValueError()
        branch = value["branch"]
        if not isinstance(branch, str) or not branch or len(branch) > 200 or any(ord(c) < 32 for c in branch):
            raise ValueError()
        if (dirty and type(value["dirty"]) is not bool) or (not dirty and value["dirty"] is not None):
            raise ValueError()
        if not isinstance(value["tracked_local"], list) or any(not isinstance(p, str) for p in value["tracked_local"]):
            raise ValueError()
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise Refusal("muse_response_invalid") from None
    return value


@dataclass(frozen=True)
class Revision:
    kind: str
    branch: str
    head: str
    source_id: str | None = None
    dirty: bool | None = None
    tracked_local: tuple[str, ...] = ()


def revision(root, config, *, dirty=False):
    if config["vcs"] == "git":
        if not os.path.lexists(root / ".git") or Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
            raise Refusal("git_repository_mismatch")
        return Revision("git", git_branch(root), git_head(root), dirty=(
            bool(git(root, "status", "--porcelain", "--untracked-files=normal")) if dirty else None))
    binding = config["muse"]
    state = muse_read(root, binding["runtime"]["python"], dirty=dirty)
    if state["repo_id"] != binding["repo_id"] or state["store"] != binding["store"]:
        raise Refusal("muse_repository_mismatch")
    if state["runtime"] != binding["runtime"]:
        raise Refusal("muse_runtime_changed: explicitly adopt the reviewed Muse runtime")
    return Revision("muse", state["branch"], state["head"], state["repo_id"],
                    state["dirty"], tuple(state["tracked_local"]))

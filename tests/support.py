"""Test helpers (not pytest fixtures)."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from adapters.config import OverseerConfig, load_config
from adapters.factory import create_adapter
from adapters.runner import CommandResult, RecordingRunner

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PILOT = FIXTURES / "pilot"
CHECKPOINTS = FIXTURES / "checkpoints"
HONESTY = FIXTURES / "honesty"
KIT_ROOT = Path(__file__).resolve().parent.parent
OVERSEER_DEPRECATION_LINE = "warning: 'overseer' is deprecated; use 'ok' (same commands).\n"


@dataclass(frozen=True)
class ShimResult:
    """Captured POSIX shim subprocess output."""

    exit_code: int
    stdout: str
    stderr: str


def seed_git_repo(repo_root: Path) -> None:
    """Initialize a minimal git repo for subprocess shim tests."""
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "seed"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


def run_shim(
    shim: str,
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> ShimResult:
    """Invoke ``cli/<shim>`` as a subprocess (§Q2A.10 integration/e2e helper)."""
    script = KIT_ROOT / "cli" / shim
    proc_env = os.environ.copy()
    if env:
        proc_env.update(env)
    completed = subprocess.run(
        [str(script), *argv],
        cwd=cwd,
        env=proc_env,
        capture_output=True,
        text=True,
        check=False,
    )
    return ShimResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def write_config(repo_root: Path, name: str) -> Path:
    src = FIXTURES / name
    dest = repo_root / ".overseer" / "config.yaml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def load_fixture_config(repo_root: Path, name: str) -> OverseerConfig:
    return load_config(write_config(repo_root, name))


def pls_config(
    repo_root: Path,
    fixture: str = "config-git-only.yaml",
    *,
    enabled: bool = True,
) -> OverseerConfig:
    """Fixture config with ``close_ritual.post_land_sync.enabled`` overridden (§PLS tests)."""
    from dataclasses import replace

    from adapters.config import PostLandSyncConfig

    config = load_fixture_config(repo_root, fixture)
    return replace(
        config,
        close_ritual=replace(
            config.close_ritual,
            post_land_sync=PostLandSyncConfig(enabled=enabled),
        ),
    )


def gh_merged_runner(*, pr_state: str = "OPEN", check_state: str = "pass"):
    """Fake ``gh`` runner driving ``run_pr_land`` to a merge outcome (§PLS tests)."""
    import json as _json
    import subprocess as _sp

    def _runner(cmd: list[str]) -> "_sp.CompletedProcess[str]":
        if cmd[:3] == ["gh", "pr", "view"]:
            return _sp.CompletedProcess(
                cmd, 0, stdout=_json.dumps({"number": 1, "state": pr_state}), stderr=""
            )
        if cmd[:3] == ["gh", "pr", "checks"]:
            rc = 0 if check_state == "pass" else 1
            return _sp.CompletedProcess(
                cmd, rc, stdout=f"verify\t{check_state}\t0s\thttps://example.test/v\n", stderr=""
            )
        if cmd[:3] == ["gh", "pr", "merge"]:
            return _sp.CompletedProcess(cmd, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected gh argv: {cmd}")

    return _runner


class FakeGitRunner:
    """Recording git fake for §PLS post-land sync argv assertions.

    ``fail`` is a set of git subcommands ({"fetch", "status", "rev-parse",
    "checkout", "pull"}) that return exit 1.
    """

    def __init__(
        self,
        *,
        porcelain: str = "",
        branch: str = "main",
        fail: set[str] | tuple[str, ...] = (),
    ) -> None:
        self.porcelain = porcelain
        self.branch = branch
        self.fail = set(fail)
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str]):
        import subprocess as _sp

        self.calls.append(list(cmd))
        op = cmd[1] if len(cmd) > 1 else ""
        rc = 1 if op in self.fail else 0
        stdout = ""
        if rc == 0:
            if op == "status":
                stdout = self.porcelain
            elif op == "rev-parse":
                stdout = self.branch + "\n"
            elif op == "checkout":
                self.branch = cmd[2]
        return _sp.CompletedProcess(
            list(cmd), rc, stdout=stdout, stderr="induced failure" if rc else ""
        )


def ok(stdout: str = "") -> CommandResult:
    return CommandResult(stdout=stdout, stderr="", exit_code=0)


def fail(stderr: str = "error", code: int = 1) -> CommandResult:
    return CommandResult(stdout="", stderr=stderr, exit_code=code)


def make_runner(responses: dict[str, CommandResult]) -> RecordingRunner:
    return RecordingRunner(responses=responses, calls=[])


class BranchStateRunner:
    """Stateful fake VCS host for §GSW write-path and §GSB reconcile tests.

    Tracks the current branch of both histories, refuses a bare Muse checkout
    of an existing branch while the Muse tree is dirty (Muse 0.2.x live
    behavior — the GSW incident), honors ``--autoshelf`` dirty-carry, and
    records every command for order assertions. ``--force`` always fails so
    any forbidden use surfaces in tests (§GSW.8).

    §GSB additions — per-branch tips (``git_tips`` / ``muse_tips``, Git SHAs
    and Muse ``sha256:`` ids in separate spaces), ancestry maps
    (``git_ancestors`` / ``muse_ancestors``: descendant → set of ancestors),
    and a shared-worktree content token. ``content_map`` maps a tip id to a
    content token (default: everything is ``content:base``); a Muse checkout
    of a branch rewrites ``worktree`` to that branch tip's content token —
    modeling the live defect where a stale Muse checkout dirties the shared
    tree so a Git checkout of the same name refuses.
    """

    def __init__(
        self,
        root: str,
        *,
        git_branch: str = "main",
        muse_branch: str = "main",
        git_dirty: bool = False,
        muse_dirty: bool = False,
        origin_main_tip: str = "cafebabe",
        muse_main_tip: str = "sha256:musetip",
        merged_prs_json: str = "[]",
        muse_rev_parse_main_values: list[str] | None = None,
        git_commit_fails: bool = False,
        muse_commit_fails: bool = False,
        existing_git_branches: set[str] | None = None,
        existing_muse_branches: set[str] | None = None,
        git_tips: dict[str, str] | None = None,
        muse_tips: dict[str, str] | None = None,
        git_ancestors: dict[str, set[str]] | None = None,
        muse_ancestors: dict[str, set[str]] | None = None,
        content_map: dict[str, str] | None = None,
        worktree: str | None = None,
    ) -> None:
        self.root = root
        self.git_branch = git_branch
        self.muse_branch = muse_branch
        self.git_dirty = git_dirty
        self.muse_dirty = muse_dirty
        self.origin_main_tip = origin_main_tip
        self.muse_main_tip = muse_main_tip
        self.merged_prs_json = merged_prs_json
        self.muse_rev_parse_main_values = list(muse_rev_parse_main_values or [])
        self.git_commit_fails = git_commit_fails
        self.muse_commit_fails = muse_commit_fails
        self.git_branches = {git_branch} | (existing_git_branches or set())
        self.muse_branches = {muse_branch} | (existing_muse_branches or set())
        self.git_tips: dict[str, str] = dict(git_tips or {})
        for name in self.git_branches:
            self.git_tips.setdefault(name, "feedface")
        self.muse_tips: dict[str, str] = dict(muse_tips or {})
        for name in self.muse_branches:
            self.muse_tips.setdefault(name, muse_main_tip)
        self.git_ancestors: dict[str, set[str]] = {
            sha: set(parents) for sha, parents in (git_ancestors or {}).items()
        }
        self.muse_ancestors: dict[str, set[str]] = {
            sha: set(parents) for sha, parents in (muse_ancestors or {}).items()
        }
        self.content_map: dict[str, str] = dict(content_map or {})
        self.worktree = (
            worktree
            if worktree is not None
            else self._content(self.git_tips[self.git_branch])
        )
        self.git_commit_count = 0
        self.muse_commit_count = 0
        self.calls: list[tuple[str, str | None]] = []

    def _content(self, tip: str | None) -> str:
        return self.content_map.get(tip or "", "content:base")

    def _git_worktree_dirty(self) -> bool:
        return self.git_dirty or self.worktree != self._content(
            self.git_tips.get(self.git_branch)
        )

    def _muse_worktree_dirty(self) -> bool:
        return self.muse_dirty or self.worktree != self._content(
            self.muse_tips.get(self.muse_branch)
        )

    def _git_known_commits(self) -> set[str]:
        known = set(self.git_tips.values()) | set(self.git_ancestors)
        for parents in self.git_ancestors.values():
            known |= parents
        return known

    def run(self, command: str, *, cwd: str | None = None) -> CommandResult:
        import shlex

        self.calls.append((command, cwd))
        tokens = shlex.split(command)
        if tokens[0] == "git":
            return self._git(tokens[1:])
        if tokens[0] == "muse":
            # muse -C <root> <args...>
            return self._muse(tokens[3:])
        if tokens[0] == "gh":
            return CommandResult(stdout=self.merged_prs_json, stderr="", exit_code=0)
        return CommandResult(stdout="", stderr="unmocked command", exit_code=127)

    def _git(self, args: list[str]) -> CommandResult:
        if args[:3] == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return _ok_result(self.git_branch)
        if args == ["rev-parse", "origin/main"]:
            return _ok_result(self.origin_main_tip)
        if args == ["rev-parse", "HEAD"]:
            return _ok_result(self.git_tips.get(self.git_branch, "feedface"))
        if args[:2] == ["rev-parse", "--verify"] and len(args) == 3:
            name = args[2].removeprefix("refs/heads/")
            if name in self.git_branches:
                return _ok_result(self.git_tips[name])
            return _fail_result(f"unknown ref {name!r}")
        if args[0] == "rev-parse" and len(args) == 2:
            name = args[1]
            if name in self.git_branches:
                return _ok_result(self.git_tips[name])
            return _fail_result(f"unknown ref {name!r}")
        if args[:2] == ["status", "--porcelain"]:
            return _ok_result(" M tracked.md" if self._git_worktree_dirty() else "")
        if args[:2] == ["checkout", "-b"]:
            branch = args[2]
            if branch in self.git_branches:
                return _fail_result(f"branch {branch!r} already exists")
            self.git_tips[branch] = self.git_tips.get(self.git_branch, "feedface")
            self.git_branches.add(branch)
            self.git_branch = branch
            return _ok_result("")
        if args[0] == "checkout":
            if "--force" in args:
                return _fail_result("--force forbidden in GSW tests")
            branch = args[-1]
            if branch not in self.git_branches:
                return _fail_result(f"unknown branch {branch!r}")
            target_content = self._content(self.git_tips.get(branch))
            current_content = self._content(self.git_tips.get(self.git_branch))
            if (
                not self.git_dirty
                and self.worktree != current_content
                and self.worktree != target_content
            ):
                # Live git two-tree rule: foreign worktree bytes that match
                # neither HEAD nor the target refuse the switch (the GSB
                # incident after a stale Muse checkout).
                return _fail_result(
                    "error: Your local changes to the following files would be "
                    "overwritten by checkout"
                )
            self.git_branch = branch  # git carries dirty changes across checkout
            self.worktree = target_content
            return _ok_result("")
        if args[:2] == ["branch", "-f"] and len(args) == 4:
            name, tip = args[2], args[3]
            if name == self.git_branch:
                return _fail_result(
                    f"cannot force update the currently checked out branch {name!r}"
                )
            self.git_branches.add(name)
            self.git_tips[name] = tip
            return _ok_result("")
        if args[0] == "update-ref" and len(args) == 3:
            name = args[1].removeprefix("refs/heads/")
            self.git_branches.add(name)
            self.git_tips[name] = args[2]
            return _ok_result("")
        if args[:2] == ["reset", "--hard"] and len(args) == 3:
            tip = args[2]
            self.git_tips[self.git_branch] = tip
            self.worktree = self._content(tip)
            self.git_dirty = False
            return _ok_result("")
        if args[0] == "add":
            return _ok_result("")
        if args[0] == "commit":
            if self.git_commit_fails:
                return _fail_result("induced git commit failure")
            self.git_commit_count += 1
            parent = self.git_tips.get(self.git_branch, "feedface")
            new_sha = f"gitc{self.git_commit_count:04d}"
            self.git_ancestors[new_sha] = {parent} | self.git_ancestors.get(parent, set())
            self.git_tips[self.git_branch] = new_sha
            self.content_map[new_sha] = self.worktree
            self.git_dirty = False
            return _ok_result("")
        if args[0] == "push":
            return _ok_result("")
        if args[:2] == ["remote", "get-url"]:
            return _ok_result("git@github.com:owner/repo.git")
        if args[:2] == ["merge-base", "--is-ancestor"] and len(args) == 4:
            ancestor, descendant = args[2], args[3]
            if ancestor == descendant or ancestor in self.git_ancestors.get(
                descendant, set()
            ):
                return _ok_result("")
            known = self._git_known_commits()
            if ancestor in known and descendant in known:
                return CommandResult(stdout="", stderr="", exit_code=1)
            # Legacy permissive default for ids outside the modeled graph
            # (e.g. realign superset probes against bridge anchors).
            return _ok_result("")
        if args[0] == "merge-base":
            return _ok_result("")
        if args[0] == "rev-list":
            return _ok_result("0")
        return CommandResult(stdout="", stderr="unmocked git command", exit_code=127)

    def _muse(self, args: list[str]) -> CommandResult:
        if args[:3] == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return _ok_result(self.muse_branch)
        if args == ["rev-parse", "main"]:
            if self.muse_rev_parse_main_values:
                return _ok_result(self.muse_rev_parse_main_values.pop(0))
            return _ok_result(self.muse_tips.get("main", self.muse_main_tip))
        if args == ["rev-parse", "HEAD"]:
            return _ok_result(self.muse_tips.get(self.muse_branch, self.muse_main_tip))
        if args[0] == "rev-parse" and len(args) == 2:
            name = args[1]
            if name in self.muse_branches:
                return _ok_result(self.muse_tips[name])
            return _fail_result(f"'{name}' not found")
        if args[:2] == ["status", "--json"]:
            dirty = self._muse_worktree_dirty()
            return _ok_result(
                json.dumps({"dirty": dirty, "total_changes": 1 if dirty else 0})
            )
        if args[:2] == ["status", "--porcelain"]:
            return _ok_result(" M tracked.md" if self._muse_worktree_dirty() else "")
        if args[:2] == ["branch", "--show-current"]:
            return _ok_result(self.muse_branch)
        if args[:2] == ["checkout", "-b"]:
            branch = args[2]
            if branch in self.muse_branches:
                return _fail_result(f"branch {branch!r} already exists")
            self.muse_tips[branch] = self.muse_tips.get(
                self.muse_branch, self.muse_main_tip
            )
            self.muse_branches.add(branch)
            self.muse_branch = branch
            return _ok_result("")
        if args[:2] == ["checkout", "--autoshelf"]:
            branch = args[2]
            if branch not in self.muse_branches:
                return _fail_result(f"unknown branch {branch!r}")
            self.muse_branch = branch  # dirty changes shelved + reapplied
            self.worktree = self._content(self.muse_tips.get(branch))
            return _ok_result("")
        if args[0] == "checkout":
            if "--force" in args:
                return _fail_result("--force forbidden in GSW tests")
            branch = args[-1]
            if branch not in self.muse_branches:
                return _fail_result(f"unknown branch {branch!r}")
            if self._muse_worktree_dirty():
                # Muse 0.2.x live behavior: refuse dirty tracked checkout.
                return _fail_result("dirty tracked files present; use --autoshelf or --merge")
            self.muse_branch = branch
            # Muse rewrites the shared worktree to the branch tip's content —
            # the live §GSB defect when that tip is stale.
            self.worktree = self._content(self.muse_tips.get(branch))
            return _ok_result("")
        if args[0] == "update-ref" and len(args) == 3:
            name = args[1]
            self.muse_branches.add(name)
            self.muse_tips[name] = args[2]
            return _ok_result("")
        if args[0] == "reset" and "--hard" in args:
            if "--force" in args:
                return _fail_result("--force forbidden in GSW tests")
            target = next(a for a in args[1:] if not a.startswith("-"))
            if self._muse_worktree_dirty():
                # Live Muse 0.2.x refuses reset --hard on tracked changes.
                return _fail_result(
                    "error: Your local changes would be overwritten by reset --hard"
                )
            self.muse_tips[self.muse_branch] = target
            self.worktree = self._content(target)
            return _ok_result("")
        if args[0] == "merge-base":
            operands = [a for a in args[1:] if not a.startswith("-")]
            if len(operands) != 2:
                return _fail_result("merge-base needs two commits")
            commit_a, commit_b = operands
            if commit_a == commit_b or commit_a in self.muse_ancestors.get(
                commit_b, set()
            ):
                base: str | None = commit_a
            elif commit_b in self.muse_ancestors.get(commit_a, set()):
                base = commit_b
            else:
                base = None
            return _ok_result(
                json.dumps(
                    {
                        "commit_a": commit_a,
                        "commit_b": commit_b,
                        "merge_base": base,
                        "exit_code": 0,
                    }
                )
            )
        if args[:2] == ["code", "add"]:
            return _ok_result("")
        if args[0] == "add":
            # Muse 0.2.x live behavior: no top-level `add` subcommand.
            return CommandResult(
                stdout="",
                stderr="muse: error: argument COMMAND: invalid choice: 'add'",
                exit_code=2,
            )
        if args[0] == "commit":
            if self.muse_commit_fails:
                return _fail_result("induced muse commit failure")
            self.muse_commit_count += 1
            parent = self.muse_tips.get(self.muse_branch, self.muse_main_tip)
            new_sha = f"sha256:musec{self.muse_commit_count:04d}"
            self.muse_ancestors[new_sha] = {parent} | self.muse_ancestors.get(
                parent, set()
            )
            self.muse_tips[self.muse_branch] = new_sha
            self.content_map[new_sha] = self.worktree
            self.muse_dirty = False
            return _ok_result("")
        if args[0] == "bridge":
            return _ok_result("")
        return CommandResult(stdout="", stderr="unmocked muse command", exit_code=127)


def _ok_result(stdout: str) -> CommandResult:
    return CommandResult(stdout=stdout, stderr="", exit_code=0)


def _fail_result(stderr: str) -> CommandResult:
    return CommandResult(stdout="", stderr=stderr, exit_code=1)


GSW_CONFIG_BY_REGIME = {
    "git-only": "config-git-only.yaml",
    "muse-only": "config-muse-only.yaml",
    "muse+git-mirror": "config-muse-git-mirror.yaml",
}

GSW_DOC_NAMES = {
    "git-only": ("OVERSEER-HANDOVER.md", "ROADMAP.md"),
    "muse-only": ("MUSEHUB-OVERSEER-HANDOVER.md", "MUSEHUB-ROADMAP.md"),
    "muse+git-mirror": ("OVERSEER-HANDOVER.md", "ROADMAP.md"),
}

_GSW_MUSE_ONLY_HANDOVER = "# Handover — muse-only\n\n## Change log\n\n- **2026-07-01** — initial\n"
_GSW_MUSE_ONLY_ROADMAP = (
    "# Roadmap — muse-only\n\n## Build queue\n\n"
    "| Phase | Model | Status | Deliverable |\n| --- | --- | --- | --- |\n"
    "| **X1** | Auto | **TODO** | thing |\n"
)


def seed_gsw_repo(
    repo_root: Path,
    regime: str,
    *,
    handover_text: str | None = None,
    roadmap_text: str | None = None,
    muse_main_tip: str = "sha256:musetip",
) -> tuple[Path, Path]:
    """Seed config, docs, and Muse substrate/bridge for §GSW write-path tests.

    Returns ``(handover_path, roadmap_path)``. Default docs produce D1 drift
    for git regimes (claim ``deadbeef`` vs actual ``cafebabe``); muse-only
    docs are minimal (its drift is driven by sequenced R2/R3 reads).
    """
    write_config(repo_root, GSW_CONFIG_BY_REGIME[regime])
    if regime != "git-only":
        seed_muse_substrate(repo_root)
    if regime == "muse+git-mirror":
        (repo_root / ".muse" / "git-bridge.toml").write_text(
            f'[last_export]\nmuse_commit_id = "{muse_main_tip}"\ngit_sha = "{"1" * 40}"\n',
            encoding="utf-8",
        )
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    handover_name, roadmap_name = GSW_DOC_NAMES[regime]
    if handover_text is None:
        if regime == "muse-only":
            handover_text = _GSW_MUSE_ONLY_HANDOVER
        else:
            handover_text = (FIXTURES / "governance-handover-drift.md").read_text(encoding="utf-8")
    if roadmap_text is None:
        if regime == "muse-only":
            roadmap_text = _GSW_MUSE_ONLY_ROADMAP
        else:
            roadmap_text = (FIXTURES / "governance-roadmap-drift.md").read_text(encoding="utf-8")
    handover_path = docs / handover_name
    roadmap_path = docs / roadmap_name
    handover_path.write_text(handover_text, encoding="utf-8")
    roadmap_path.write_text(roadmap_text, encoding="utf-8")
    return handover_path, roadmap_path


def gsw_runner(repo_root: Path, regime: str, **kwargs) -> BranchStateRunner:
    """``BranchStateRunner`` pre-configured per regime for §GSW tests.

    muse-only drives its only possible drift dimension (D2) via sequenced
    ``muse rev-parse main`` values (R2 anchor read, then R3 canonical read).
    """
    if regime == "muse-only" and "muse_rev_parse_main_values" not in kwargs:
        kwargs["muse_rev_parse_main_values"] = ["sha256:anchor", "sha256:moved"]
    return BranchStateRunner(str(repo_root.resolve()), **kwargs)


def adapter_for(config: OverseerConfig, repo_root: Path, runner: RecordingRunner):
    return create_adapter(config, repo_root, runner=runner)


def git_status_runner(
    branch: str = "main",
    dirty: bool = False,
    tip: str = "cafebabe",
) -> RecordingRunner:
    """Recording runner with git-only ``status()`` + origin/main tip responses."""
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            "git rev-parse --abbrev-ref HEAD": ok(branch),
            "git status --porcelain": ok(dirty_out),
            "git rev-parse origin/main": ok(tip),
        }
    )


def muse_status_runner(
    repo_root: Path,
    branch: str = "main",
    dirty: bool = False,
    tip: str = "cafebabe",
) -> RecordingRunner:
    """Recording runner with muse-only ``status()`` responses."""
    root = str(repo_root.resolve())
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            f"muse -C {root} branch --show-current": ok(branch),
            f"muse -C {root} status --porcelain": ok(dirty_out),
            f"muse -C {root} rev-parse {branch}": ok(tip),
            f"muse -C {root} rev-parse main": ok(tip),
        }
    )


def muse_mirror_status_runner(
    repo_root: Path,
    branch: str = "main",
    dirty: bool = False,
    tip: str = "cafebabe",
) -> RecordingRunner:
    """Recording runner with muse+git-mirror ``status()`` responses."""
    root = str(repo_root.resolve())
    dirty_out = " M file" if dirty else ""
    return make_runner(
        {
            f"muse -C {root} rev-parse --abbrev-ref HEAD": ok(branch),
            f"muse -C {root} status --porcelain": ok(dirty_out),
            f"muse -C {root} status --json": ok(
                '{"dirty": true}' if dirty else '{"dirty": false}'
            ),
            "git rev-parse --abbrev-ref HEAD": ok(branch),
            "git status --porcelain": ok(dirty_out),
            "git rev-parse origin/main": ok(tip),
            f"muse -C {root} rev-parse main": ok(tip),
            f"muse -C {root} rev-parse {branch}": ok(tip),
        }
    )


def seed_governance_freshness(
    repo_root: Path,
    tip: str = "cafebabe",
    *,
    handover_path: Path | None = None,
) -> None:
    """Align default-lane handover GitHub-main claim + write enriched marker (§GFG).

    Call after ``ok init`` so ``status --exit-code`` is not fail-closed solely on freshness.
    """
    from datetime import datetime, timezone

    from adapters.config import load_config, resolve_lane_docs
    from cli.docs_paths import lane_living_doc_abs
    from cli.paths import resolve_config_path

    config_path = resolve_config_path(repo_root, None)
    config = load_config(config_path)
    lane = config.docs.default_lane if config.docs.lanes is not None else None
    lane_docs = resolve_lane_docs(config, lane)
    path = handover_path or lane_living_doc_abs(
        repo_root, config, lane_docs, lane_docs.handover
    )
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        claim = f"| GitHub `main` | `{tip}` |"
        if f"`{tip}`" not in text or "GitHub `main`" not in text:
            text = text.rstrip() + f"\n\n| Item | Value |\n| --- | --- |\n{claim}\n"
            path.write_text(text, encoding="utf-8")

    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    marker = repo_root / ".overseer" / "last_governance_sync"
    marker.parent.mkdir(parents=True, exist_ok=True)
    r1 = "" if config.vcs.regime == "muse-only" else tip
    r3 = tip
    marker.write_text(f"{stamp}\nr1={r1}\nr3={r3}\n", encoding="utf-8")

    if config.vcs.regime == "muse+git-mirror":
        muse_dir = repo_root / ".muse"
        muse_dir.mkdir(parents=True, exist_ok=True)
        bridge = muse_dir / "git-bridge.toml"
        # muse_commit_id = tip (R2 Muse space); git_sha uses a distinct 40-hex so
        # fixtures prove git_sha≠tip alone is not D2 drift (§D2F.3).
        git_export = "1" * 40 if tip.startswith("sha256:") else tip
        bridge.write_text(
            f'[last_export]\n'
            f'muse_commit_id = "{tip}"\n'
            f'git_sha = "{git_export}"\n',
            encoding="utf-8",
        )


LAND_A_MARKER = (
    "<!-- overseer:next role=primary lane=product status=live land-phase=land-a -->"
)
LAND_B_MARKER = (
    "<!-- overseer:next role=primary lane=product status=live land-phase=land-b -->"
)


def land_a_fence_body(slice_id: str = "PMHF", *, paste_extra: str = "") -> str:
    """Frozen land-a paste body (§PMHF.3.1) for fixtures."""
    return (
        "Model: Operator + Auto\n"
        f"ID: {slice_id} → main (land-a)\n"
        "land-phase: land-a\n"
        "\n"
        "Deliver:\n"
        "1. Open/update PR (or SD-21 authorized land path)\n"
        "2. Stop for Tier 3 merge authorization when required\n"
        "3. Do NOT claim land complete\n"
        "4. Do NOT regenerate post-merge NEXT in this paste\n"
        f"{paste_extra}"
        "\n"
        "After merge is confirmed on main: paste land-b (same slice). "
        "Land is incomplete until land-b.\n"
    )


def land_b_fence_body(slice_id: str = "PMHF") -> str:
    """Frozen land-b paste body (§PMHF.3.2) for fixtures."""
    return (
        "Model: Auto\n"
        f"ID: {slice_id} land-b (post-merge sync)\n"
        "land-phase: land-b\n"
        "\n"
        "Deliver:\n"
        "1. Fetch/pull latest main (regime-appropriate)\n"
        "2. ok governance-sync --dry-run then apply when the plan is correct\n"
        "3. Regenerate NEXT + paste so they no longer say wait-for-merge / land-a\n"
        "4. Feature-branch commit bundling ROADMAP + HANDOVER (SD-17)\n"
        "5. ok status --exit-code → 0 and ok land-closeout → 0 before claiming land complete\n"
    )


def land_handover_text(
    claim: str = "cafebabe",
    *,
    marker: str | None = LAND_A_MARKER,
    slice_id: str = "PMHF",
    heading: str | None = None,
    fence_body: str | None = None,
) -> str:
    """Handover fixture with NEXT marker, paste fence, and GitHub-main claim (§PMHF)."""
    if fence_body is None:
        fence_body = land_a_fence_body(slice_id)
    if heading is None:
        heading = f"{slice_id} → main (land-a)"
    marker_line = f"{marker}\n" if marker else ""
    return (
        "# Overseer Handover — fixture\n"
        "\n"
        f"{marker_line}## NEXT SESSION — {heading}\n"
        "\n"
        "**Model:** Operator + Auto\n"
        "\n"
        "### What just landed\n"
        "\n"
        "| Slice | Deliverable |\n"
        "| --- | --- |\n"
        "| prior | prior slice |\n"
        "\n"
        "### THE ONE NEXT STEP — **Model: Operator + Auto**\n"
        "\n"
        "| | |\n"
        "| --- | --- |\n"
        f"| **ID** | **{heading}** |\n"
        "\n"
        f"### Paste-ready prompt — {slice_id}\n"
        "\n"
        "```text\n"
        f"{fence_body}"
        "```\n"
        "\n"
        "---\n"
        "\n"
        "## Verified snapshot\n"
        "\n"
        "| Area | State |\n"
        "| --- | --- |\n"
        "| **VCS regime** | `git-only` |\n"
        "\n"
        "<!-- overseer:anchor:vcs-table -->\n"
        "## VCS (verified 2026-07-30)\n"
        "\n"
        "| Item | Value |\n"
        "| --- | --- |\n"
        "| Branch | `main` |\n"
        f"| GitHub `main` | `{claim}` |\n"
        "<!-- /overseer:anchor:vcs-table -->\n"
        "\n"
        "## Change log\n"
        "\n"
        "- **2026-07-30** — land-a opened\n"
    )


def land_roadmap_text(*rows: str) -> str:
    """Roadmap fixture with a build queue; pass full ``| … |`` rows."""
    default_rows = (
        "| **PMHF-b Build** | Auto | **DONE** | land closeout build |",
        "| **PMHF → main** | Operator + Auto | **TODO** | Land PMHF (Tier 3 merge) |",
    )
    body = "\n".join(rows or default_rows)
    return (
        "# Roadmap — fixture\n"
        "\n"
        "## Build queue\n"
        "\n"
        "| Phase | Model | Status | Deliverable |\n"
        "| --- | --- | --- | --- |\n"
        f"{body}\n"
        "\n"
        "## Definition of Done (every phase)\n"
        "\n"
        "- Tests green\n"
    )


def seed_land_repo(
    repo_root: Path,
    *,
    claim: str = "cafebabe",
    handover_text: str | None = None,
    roadmap_text: str | None = None,
    marker_tip: str | None = "cafebabe",
) -> None:
    """Seed config, lock, docs, and enriched sync marker for land-closeout tests."""
    write_config(repo_root, "config-git-only.yaml")
    (repo_root / ".overseer" / "version.lock").write_text(
        "lock_version: 1\nkit_version: 0.1.0\nconfig_version: 1\n"
        "footprint_digest: sha256:" + ("0" * 64) + "\n"
        'installed_at: "2026-01-01T00:00:00Z"\nsynced_at: "2026-01-01T00:00:00Z"\n'
        "footprint: []\n",
        encoding="utf-8",
    )
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "OVERSEER-HANDOVER.md").write_text(
        handover_text if handover_text is not None else land_handover_text(claim),
        encoding="utf-8",
    )
    (docs / "ROADMAP.md").write_text(
        roadmap_text if roadmap_text is not None else land_roadmap_text(),
        encoding="utf-8",
    )
    if marker_tip is not None:
        (repo_root / ".overseer" / "last_governance_sync").write_text(
            f"2026-07-30T00:00:00Z\nr1={marker_tip}\nr3={marker_tip}\n",
            encoding="utf-8",
        )


def run_cli(
    argv: list[str],
    *,
    cwd: Path,
    runner: RecordingRunner | None = None,
    kit: Path | None = None,
    review_provider_factory=None,
    script_executor=None,
    json_mode: bool = False,
) -> int:
    """Invoke ``cli.main`` with an injected runner and working directory."""
    from cli.context import CliContext
    from cli.main import main
    from cli.output import OutputContext

    old_cwd = Path.cwd()
    os.chdir(cwd)
    try:
        ctx = CliContext.create(
            runner=runner or make_runner({}),
            cwd=cwd,
            kit=kit,
            output=OutputContext(json_mode=json_mode),
            review_provider_factory=review_provider_factory,
            script_executor=script_executor,
        )
        return main(argv, ctx=ctx)
    finally:
        os.chdir(old_cwd)


def seed_muse_substrate(repo_root: Path) -> None:
    """Create minimal healthy ``.muse/`` for muse-backed regime tests."""
    muse = repo_root / ".muse"
    muse.mkdir(parents=True, exist_ok=True)
    (muse / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (muse / "repo.json").write_text("{}", encoding="utf-8")
    (muse / "config.toml").write_text("", encoding="utf-8")


def seed_freeze_repo(repo_root: Path, *, config_name: str = "config-git-only.yaml") -> Path:
    """Write config and copy a freeze artifact fixture into a temp repo."""
    write_config(repo_root, config_name)
    if "muse" in config_name:
        seed_muse_substrate(repo_root)
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    artifact = docs / "FREEZE.md"
    artifact.write_text((FIXTURES / "freeze-artifact.md").read_text(encoding="utf-8"), encoding="utf-8")
    return artifact


def pass_provider_factory():
    """Factory returning a provider that always passes."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(scripted_findings=[])

    return _factory


def findings_provider_factory(findings):
    """Factory returning a provider with scripted findings."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(scripted_findings=list(findings))

    return _factory


def unreachable_provider_factory(cause: str = "offline"):
    """Factory returning an unreachable local provider."""
    from tools.freeze_reviewer.providers.base import LocalReviewProvider

    def _factory(_provider_name: str) -> LocalReviewProvider:
        return LocalReviewProvider(force_unreachable=True, unreachable_cause=cause)

    return _factory


class FakeHttpTransport:
    """Recording HTTP transport for API provider tests (no network)."""

    def __init__(
        self,
        *,
        health_status: int = 200,
        health_body: bytes = b'{"status":"ok"}',
        review_status: int = 200,
        review_body: bytes | None = None,
        fail_health: bool = False,
        fail_review: bool = False,
    ) -> None:
        self.health_status = health_status
        self.health_body = health_body
        self.review_status = review_status
        self.review_body = review_body or b'{"findings":[]}'
        self.fail_health = fail_health
        self.fail_review = fail_review
        self.calls: list[dict] = []

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None = None,
        timeout: float = 30.0,
    ) -> tuple[int, bytes]:
        from tools.freeze_reviewer.providers.api_client import ProviderTransportError

        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": body,
            }
        )
        if "/health" in url:
            if self.fail_health:
                raise ProviderTransportError("health transport failure")
            return self.health_status, self.health_body
        if self.fail_review:
            raise ProviderTransportError("review transport failure")
        return self.review_status, self.review_body


def api_provider_factory(transport: FakeHttpTransport):
    """Factory returning an API provider wired to a fake HTTP transport."""
    from tools.freeze_reviewer.providers.api_client import ReviewApiClient
    from tools.freeze_reviewer.providers.base import ApiReviewProvider

    def _factory(_provider_name: str) -> ApiReviewProvider:
        client = ReviewApiClient(transport=transport)
        return ApiReviewProvider(client=client)

    return _factory


def api_unreachable_provider_factory(cause: str = "API provider unavailable"):
    """Factory returning a forced-unreachable API provider."""
    from tools.freeze_reviewer.providers.base import ApiReviewProvider

    def _factory(_provider_name: str) -> ApiReviewProvider:
        return ApiReviewProvider(force_unreachable=True, unreachable_cause=cause)

    return _factory


def seed_checkpoint_repo(repo_root: Path) -> None:
    """Copy checkpoint fixture pack into a temp repo and mark scripts executable."""
    import shutil
    import stat

    (repo_root / ".overseer").mkdir(parents=True, exist_ok=True)
    config_src = CHECKPOINTS / "config-checkpoints-enabled.yaml"
    (repo_root / ".overseer" / "config.yaml").write_text(
        config_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for rel in ("policy", "manifests", "scripts"):
        src = CHECKPOINTS / rel
        dest = repo_root / rel
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    for script in (repo_root / "scripts" / "verify").glob("*.py"):
        script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def load_checkpoint_config(repo_root: Path) -> OverseerConfig:
    """Load checkpoint-enabled config from a seeded repo."""
    seed_checkpoint_repo(repo_root)
    return load_config(repo_root / ".overseer" / "config.yaml")


def seed_honesty_repo(repo_root: Path) -> None:
    """Copy honesty fixture pack into a temp repo."""
    import shutil

    (repo_root / ".overseer").mkdir(parents=True, exist_ok=True)
    config_src = HONESTY / "config-honesty-enabled.yaml"
    (repo_root / ".overseer" / "config.yaml").write_text(
        config_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for rel in ("artifacts", "entries"):
        src = HONESTY / rel
        dest = repo_root / rel
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)


def load_honesty_config(repo_root: Path) -> OverseerConfig:
    """Load honesty-enabled config from a seeded repo."""
    seed_honesty_repo(repo_root)
    return load_config(repo_root / ".overseer" / "config.yaml")


def honesty_artifact_hash(repo_root: Path) -> str:
    """SHA-256 of the fixture sample artifact."""
    from tools.honesty.artifact import sha256_file_bytes

    return sha256_file_bytes(repo_root / "artifacts" / "sample.txt")


def load_honesty_entry(repo_root: Path, name: str, *, artifact_hash: str | None = None) -> dict:
    """Load a verdict entry fixture with artifact hash substituted."""
    import json

    text = (HONESTY / "entries" / name).read_text(encoding="utf-8")
    if artifact_hash is None:
        artifact_hash = honesty_artifact_hash(repo_root)
    text = text.replace("PLACEHOLDER", artifact_hash)
    return json.loads(text)


def seed_pilot_tree(
    repo_root: Path,
    *,
    handover_rel: str,
    handover_text: str = "# Hand preserved handover\n",
    roadmap_rel: str | None = None,
    roadmap_text: str | None = None,
    extra_cursor_rules: dict[str, str] | None = None,
) -> None:
    """Create a pre-existing living-doc layout for migrate fixtures."""
    hand = repo_root / handover_rel
    hand.parent.mkdir(parents=True, exist_ok=True)
    hand.write_text(handover_text, encoding="utf-8")
    if roadmap_rel is not None:
        road = repo_root / roadmap_rel
        road.parent.mkdir(parents=True, exist_ok=True)
        road.write_text(roadmap_text or "# Hand preserved roadmap\n", encoding="utf-8")
    if extra_cursor_rules:
        rules = repo_root / ".cursor" / "rules"
        rules.mkdir(parents=True, exist_ok=True)
        for name, text in extra_cursor_rules.items():
            (rules / name).write_text(text, encoding="utf-8")


def lock_origins(repo_root: Path) -> dict[str, str]:
    """Return path → origin map from ``version.lock``."""
    from cli.version_lock import entry_origin, read_version_lock

    lock = read_version_lock(repo_root / ".overseer" / "version.lock")
    return {e.path: entry_origin(e) for e in lock.footprint}


def generate_ed25519_keypair() -> tuple[object, str]:
    """Return ``(private_key, ed25519:<base64> pubkey token)`` for tests only."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from tools.honesty.ed25519_util import encode_ed25519_token

    private_key = Ed25519PrivateKey.generate()
    pubkey_token = encode_ed25519_token(private_key.public_key().public_bytes_raw())
    return private_key, pubkey_token


def sign_entry_hash(private_key: object, entry_hash_hex: str) -> str:
    """Sign lowercase hex ``entry_hash_hex``; return ``ed25519:<base64>`` token (tests only)."""
    from tools.honesty.ed25519_util import encode_ed25519_token

    sig_bytes = private_key.sign(entry_hash_hex.encode("utf-8"))  # type: ignore[attr-defined]
    return encode_ed25519_token(sig_bytes)


def attach_signed_provenance(
    body: dict,
    *,
    pubkey_token: str,
    agent_id: str = "cursor-agent",
    model_id: str = "gpt-5.6",
    human_ref: str | None = None,
) -> dict:
    """Return a copy of ``body`` with unsigned provenance identity fields."""
    provenance: dict = {"agent_id": agent_id, "model_id": model_id}
    if human_ref is not None:
        provenance["human_ref"] = human_ref
    signed = dict(body)
    signed["provenance"] = provenance
    signed["_test_pubkey"] = pubkey_token
    return signed


def sign_append_body(
    body: dict,
    *,
    kind: str,
    prev_hash: str,
    private_key: object,
    pubkey_token: str | None = None,
) -> dict:
    """Validate, hash, sign, and return an append-ready body with ``provenance.sig``."""
    from tools.honesty.validate import validate_append_body

    pubkey = pubkey_token or body.pop("_test_pubkey", None)
    if pubkey is None:
        raise ValueError("pubkey_token required")
    draft = dict(body)
    draft.pop("_test_pubkey", None)
    validated = validate_append_body(kind=kind, body=draft)
    preview = dict(validated)
    preview["prev_hash"] = prev_hash
    preview["provenance"] = {**validated["provenance"], "pubkey": pubkey}
    entry_hash = compute_entry_hash(preview)
    signed = dict(validated)
    signed["provenance"] = {
        **validated["provenance"],
        "pubkey": pubkey,
        "sig": sign_entry_hash(private_key, entry_hash),
    }
    return signed


def compute_entry_hash(body: dict) -> str:
    """Re-export for tests building signing previews."""
    from tools.honesty.canonical import compute_entry_hash as _compute

    return _compute(body)


def finalize_signed_body(body: dict, *, private_key: object, prev_hash: str) -> dict:
    """Compute envelope hashes and attach ``provenance.sig`` (tests / direct ledger writes)."""
    from tools.honesty.canonical import compute_entry_hash
    from tools.honesty.genesis import utc_now_z

    entry = dict(body)
    if not entry.get("ts"):
        entry["ts"] = utc_now_z()
    entry["prev_hash"] = prev_hash
    entry_hash = compute_entry_hash(entry)
    entry["entry_hash"] = entry_hash
    provenance = dict(entry.get("provenance", {}))
    provenance["sig"] = sign_entry_hash(private_key, entry_hash)
    entry["provenance"] = provenance
    return entry


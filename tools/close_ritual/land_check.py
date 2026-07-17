"""Close-ritual land check — compare require_paths to origin/main (never merge)."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from adapters.config import CloseRitualConfig, OverseerConfig


@dataclass(frozen=True)
class LandCheckResult:
    """Outcome of ``ok land-check``."""

    exit_code: int
    landed: bool
    mode: str
    ref: str
    paths: tuple[dict[str, Any], ...]
    dirty_paths: tuple[str, ...]
    messages: tuple[str, ...]
    auto_merge: bool = False  # always False — Tier 3


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )


def compare_paths_to_main(
    repo_root: Path,
    paths: tuple[str, ...],
    *,
    remote: str,
    main_branch: str,
) -> tuple[str, list[dict[str, Any]], list[str]]:
    """Return (ref, path_reports, dirty_paths)."""
    ref = f"{remote}/{main_branch}"
    if _git(repo_root, "rev-parse", "--verify", ref).returncode != 0:
        if _git(repo_root, "rev-parse", "--verify", main_branch).returncode == 0:
            ref = main_branch
        else:
            return ref, [], list(paths)

    reports: list[dict[str, Any]] = []
    for rel in paths:
        wt_path = repo_root / rel
        wt = _sha256_bytes(wt_path.read_bytes()) if wt_path.is_file() else None
        shown = _git(repo_root, "show", f"{ref}:{rel}")
        main_sha = _sha256_bytes(shown.stdout.encode("utf-8")) if shown.returncode == 0 else None
        reports.append(
            {
                "path": rel,
                "workingTreeSha256": wt,
                "mainSha256": main_sha,
                "match": wt is not None and main_sha is not None and wt == main_sha,
            }
        )

    dirty = _git(repo_root, "status", "--porcelain", "--", *paths)
    dirty_paths = [line[3:].strip() for line in dirty.stdout.splitlines() if line.strip()]
    return ref, reports, dirty_paths


def run_land_check(
    config: OverseerConfig,
    repo_root: Path,
    *,
    mode: str | None = None,
    emit: Callable[[str], None] | None = None,
) -> LandCheckResult:
    """Run close_ritual land check. Never merges to main."""
    ritual: CloseRitualConfig = config.close_ritual
    messages: list[str] = []

    def _emit(line: str) -> None:
        messages.append(line)
        if emit:
            emit(line)

    if not ritual.enabled:
        _emit("close_ritual.enabled is false — land-check is a no-op (exit 0)")
        return LandCheckResult(
            exit_code=0,
            landed=True,
            mode=mode or ritual.mode,
            ref="",
            paths=(),
            dirty_paths=(),
            messages=tuple(messages),
        )

    effective_mode = mode or ritual.mode
    if effective_mode not in {"verify_landed", "prepare_pr"}:
        _emit(f"unsupported land-check mode: {effective_mode}")
        return LandCheckResult(
            exit_code=2,
            landed=False,
            mode=effective_mode,
            ref="",
            paths=(),
            dirty_paths=(),
            messages=tuple(messages),
        )

    if ritual.consumer_verify_script:
        script = repo_root / ritual.consumer_verify_script
        if not script.is_file():
            _emit(f"consumer_verify_script missing: {ritual.consumer_verify_script}")
            return LandCheckResult(
                exit_code=1,
                landed=False,
                mode=effective_mode,
                ref="",
                paths=(),
                dirty_paths=(),
                messages=tuple(messages),
            )
        completed = subprocess.run(
            ["python3", str(script)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        out = (completed.stdout or completed.stderr or "").strip()
        if out:
            _emit(out)
        _emit("note: ok land-check never auto-merges (Tier 3)")
        return LandCheckResult(
            exit_code=completed.returncode,
            landed=completed.returncode == 0,
            mode=effective_mode,
            ref="consumer_script",
            paths=(),
            dirty_paths=(),
            messages=tuple(messages),
        )

    paths = ritual.require_paths
    if not paths:
        _emit("close_ritual.require_paths is empty — configure paths or consumer_verify_script")
        return LandCheckResult(
            exit_code=2,
            landed=False,
            mode=effective_mode,
            ref="",
            paths=(),
            dirty_paths=(),
            messages=tuple(messages),
        )

    remote = config.vcs.git.remote
    main_branch = config.vcs.git.main_branch
    ref, reports, dirty_paths = compare_paths_to_main(
        repo_root,
        paths,
        remote=remote,
        main_branch=main_branch,
    )
    all_match = all(r.get("match") for r in reports) and not dirty_paths

    if effective_mode == "prepare_pr":
        if dirty_paths:
            _emit("prepare_pr: dirty require_paths — commit before opening PR")
            for d in dirty_paths:
                _emit(f"  dirty: {d}")
            _emit("Tier 3: human merges to main; agents must not auto-merge")
            return LandCheckResult(
                exit_code=1,
                landed=False,
                mode=effective_mode,
                ref=ref,
                paths=tuple(reports),
                dirty_paths=tuple(dirty_paths),
                messages=tuple(messages),
            )
        _emit("prepare_pr: require_paths clean — push feature branch and open PR")
        _emit("Tier 3: human merges to main; agents must not auto-merge")
        return LandCheckResult(
            exit_code=0,
            landed=False,
            mode=effective_mode,
            ref=ref,
            paths=tuple(reports),
            dirty_paths=(),
            messages=tuple(messages),
        )

    # verify_landed
    if not all_match:
        _emit(f"verify_landed: FAIL — paths do not match {ref}")
        for r in reports:
            if not r.get("match"):
                _emit(f"  mismatch: {r['path']}")
        for d in dirty_paths:
            _emit(f"  dirty: {d}")
        _emit("Tier 3: human merges to main; agents must not auto-merge")
        return LandCheckResult(
            exit_code=1,
            landed=False,
            mode=effective_mode,
            ref=ref,
            paths=tuple(reports),
            dirty_paths=tuple(dirty_paths),
            messages=tuple(messages),
        )

    _emit(f"verify_landed: PASS — require_paths match {ref}")
    _emit("Tier 3: human merges to main; agents must not auto-merge")
    return LandCheckResult(
        exit_code=0,
        landed=True,
        mode=effective_mode,
        ref=ref,
        paths=tuple(reports),
        dirty_paths=(),
        messages=tuple(messages),
    )

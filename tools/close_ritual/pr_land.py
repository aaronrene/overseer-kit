"""Authorized wait-for-green PR land (Tier-3 operator-delegated).

``ok land-check`` only verifies paths vs main — it never merges.

``ok pr-land`` is the complementary close-ritual command: after the operator
authorizes a specific land (``--authorized "<reason>"``), poll GitHub checks
until they settle, refuse merge on failure (exit 2 for babysit/fix), and
merge only when green.

Why not ``gh pr merge --auto`` alone?
  Auto-merge waits only for **required** status checks. Repos without branch
  protection merge immediately. This module always polls locally first.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_CHECKS_FAILED = 2
EXIT_UNAUTHORIZED = 3
EXIT_TIMEOUT = 4
EXIT_GH_ERROR = 5

_FAIL_STATES = frozenset(
    {"fail", "failure", "cancelled", "timed_out", "action_required", "stale", "error"}
)
_PASS_STATES = frozenset({"pass", "success", "neutral", "skipped"})
_PENDING_STATES = frozenset(
    {"pending", "queued", "in_progress", "waiting", "requested", "pending_deployment"}
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class CheckRow:
    """One row from ``gh pr checks``."""

    name: str
    state: str
    elapsed: str = ""
    url: str = ""
    description: str = ""

    @property
    def normalized_state(self) -> str:
        return (self.state or "").strip().lower()

    @property
    def is_pending(self) -> bool:
        return self.normalized_state in _PENDING_STATES or self.normalized_state == ""

    @property
    def is_fail(self) -> bool:
        return self.normalized_state in _FAIL_STATES

    @property
    def is_pass(self) -> bool:
        return self.normalized_state in _PASS_STATES


@dataclass
class PrLandResult:
    """Outcome of ``ok pr-land``."""

    exit_code: int
    pr: str
    authorized: bool
    authorization: str
    merged: bool
    already_merged: bool
    checks: list[dict[str, str]] = field(default_factory=list)
    failing: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)
    merge_method: str = "squash"
    recorded_at: str = field(default_factory=_iso_now)
    auto_merge: bool = False  # always False — we poll then merge; never blind auto

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _default_runner(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def parse_gh_checks_table(text: str) -> list[CheckRow]:
    """Parse ``gh pr checks`` output into CheckRow list."""
    rows: list[CheckRow] = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t") if "\t" in line else line.split()
        if len(parts) < 2:
            continue
        rows.append(
            CheckRow(
                name=parts[0].strip(),
                state=parts[1].strip(),
                elapsed=parts[2].strip() if len(parts) > 2 else "",
                url=parts[3].strip() if len(parts) > 3 else "",
                description="\t".join(parts[4:]).strip() if len(parts) > 4 else "",
            )
        )
    return rows


def classify_checks(rows: list[CheckRow]) -> tuple[list[CheckRow], list[CheckRow], list[CheckRow]]:
    """Return (passing, failing, pending). Unknown states → pending (fail closed)."""
    passing = [r for r in rows if r.is_pass]
    failing = [r for r in rows if r.is_fail]
    pending = [r for r in rows if not r.is_pass and not r.is_fail]
    return passing, failing, pending


def fetch_pr_state(pr: str, *, runner: Runner = _default_runner) -> dict[str, Any]:
    completed = runner(
        [
            "gh",
            "pr",
            "view",
            str(pr),
            "--json",
            "number,state,url,mergeable,mergeStateStatus",
        ]
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "gh pr view failed").strip())
    return json.loads(completed.stdout)


def fetch_checks(pr: str, *, runner: Runner = _default_runner) -> list[CheckRow]:
    completed = runner(["gh", "pr", "checks", str(pr)])
    rows = parse_gh_checks_table(completed.stdout or "")
    if completed.returncode != 0 and not rows and (completed.stderr or "").strip():
        err = (completed.stderr or completed.stdout or "gh pr checks failed").strip()
        if "no checks" not in err.lower():
            raise RuntimeError(err)
    return rows


def merge_pr(pr: str, *, method: str = "squash", runner: Runner = _default_runner) -> None:
    flag = {"squash": "--squash", "merge": "--merge", "rebase": "--rebase"}.get(method)
    if flag is None:
        raise ValueError(f"unsupported merge method: {method}")
    completed = runner(["gh", "pr", "merge", str(pr), flag])
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "gh pr merge failed").strip())


def wait_for_checks(
    pr: str,
    *,
    poll_seconds: float = 20.0,
    timeout_seconds: float = 1800.0,
    allow_empty_checks: bool = False,
    runner: Runner = _default_runner,
    sleep_fn: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.monotonic,
    emit: Callable[[str], None] | None = None,
) -> PrLandResult:
    """Poll until checks settle. Does not merge."""
    messages: list[str] = []

    def _emit(line: str) -> None:
        messages.append(line)
        if emit:
            emit(line)

    deadline = now_fn() + timeout_seconds
    last_rows: list[CheckRow] = []

    while True:
        try:
            rows = fetch_checks(pr, runner=runner)
        except RuntimeError as exc:
            _emit(f"gh error: {exc}")
            return PrLandResult(
                exit_code=EXIT_GH_ERROR,
                pr=str(pr),
                authorized=True,
                authorization="",
                merged=False,
                already_merged=False,
                messages=messages,
            )

        last_rows = rows
        passing, failing, pending = classify_checks(rows)

        if not rows:
            if allow_empty_checks:
                _emit("no checks reported — allow_empty_checks=true; treating as pass")
                return PrLandResult(
                    exit_code=EXIT_OK,
                    pr=str(pr),
                    authorized=True,
                    authorization="",
                    merged=False,
                    already_merged=False,
                    messages=messages,
                )
            _emit("no checks reported yet — waiting")
        elif failing:
            names = [r.name for r in failing]
            _emit(f"checks FAILED: {', '.join(names)}")
            return PrLandResult(
                exit_code=EXIT_CHECKS_FAILED,
                pr=str(pr),
                authorized=True,
                authorization="",
                merged=False,
                already_merged=False,
                checks=[asdict(r) for r in rows],
                failing=names,
                pending=[r.name for r in pending],
                messages=messages,
            )
        elif pending or not rows:
            _emit(f"waiting: {len(passing)} pass, {len(pending) if rows else '?'} pending")
        else:
            _emit(f"all checks passed ({len(passing)})")
            return PrLandResult(
                exit_code=EXIT_OK,
                pr=str(pr),
                authorized=True,
                authorization="",
                merged=False,
                already_merged=False,
                checks=[asdict(r) for r in rows],
                messages=messages,
            )

        if now_fn() >= deadline:
            _emit(f"timeout after {timeout_seconds:.0f}s waiting for checks")
            return PrLandResult(
                exit_code=EXIT_TIMEOUT,
                pr=str(pr),
                authorized=True,
                authorization="",
                merged=False,
                already_merged=False,
                checks=[asdict(r) for r in last_rows],
                pending=[r.name for r in classify_checks(last_rows)[2]],
                messages=messages,
            )
        sleep_fn(poll_seconds)


def run_pr_land(
    pr: str,
    *,
    authorization: str,
    merge_method: str = "squash",
    poll_seconds: float = 20.0,
    timeout_seconds: float = 1800.0,
    allow_empty_checks: bool = False,
    dry_run: bool = False,
    runner: Runner = _default_runner,
    sleep_fn: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.monotonic,
    emit: Callable[[str], None] | None = None,
    repo_root: Path | None = None,  # reserved for future cwd-bound gh
) -> PrLandResult:
    """Authorize → wait for green → merge. Fail closed without authorization."""
    del repo_root  # reserved
    reason = (authorization or "").strip()
    if not reason:
        msg = (
            "Tier 3: refused — pass --authorized \"<operator reason>\" "
            "to land after green checks"
        )
        if emit:
            emit(msg)
        return PrLandResult(
            exit_code=EXIT_UNAUTHORIZED,
            pr=str(pr),
            authorized=False,
            authorization="",
            merged=False,
            already_merged=False,
            messages=[msg],
        )

    messages: list[str] = [f"authorized: {reason}"]

    def _emit(line: str) -> None:
        messages.append(line)
        if emit:
            emit(line)

    _emit(f"pr-land start pr={pr} method={merge_method} dry_run={dry_run}")

    try:
        state = fetch_pr_state(pr, runner=runner)
    except RuntimeError as exc:
        _emit(f"gh error: {exc}")
        return PrLandResult(
            exit_code=EXIT_GH_ERROR,
            pr=str(pr),
            authorized=True,
            authorization=reason,
            merged=False,
            already_merged=False,
            messages=messages,
            merge_method=merge_method,
        )

    pr_state = str(state.get("state") or "").upper()
    if pr_state == "MERGED":
        wait = wait_for_checks(
            pr,
            poll_seconds=poll_seconds,
            timeout_seconds=min(timeout_seconds, 120.0),
            allow_empty_checks=True,
            runner=runner,
            sleep_fn=sleep_fn,
            now_fn=now_fn,
            emit=_emit,
        )
        if wait.exit_code == EXIT_CHECKS_FAILED:
            _emit("PR already MERGED but checks report failure — investigate")
            return PrLandResult(
                exit_code=EXIT_CHECKS_FAILED,
                pr=str(pr),
                authorized=True,
                authorization=reason,
                merged=True,
                already_merged=True,
                checks=wait.checks,
                failing=wait.failing,
                messages=messages,
                merge_method=merge_method,
            )
        _emit("PR already MERGED")
        return PrLandResult(
            exit_code=EXIT_OK,
            pr=str(pr),
            authorized=True,
            authorization=reason,
            merged=True,
            already_merged=True,
            checks=wait.checks,
            messages=messages,
            merge_method=merge_method,
        )

    if pr_state not in {"OPEN", ""}:
        _emit(f"refused: PR state is {pr_state or 'unknown'}")
        return PrLandResult(
            exit_code=EXIT_USAGE,
            pr=str(pr),
            authorized=True,
            authorization=reason,
            merged=False,
            already_merged=False,
            messages=messages,
            merge_method=merge_method,
        )

    wait = wait_for_checks(
        pr,
        poll_seconds=poll_seconds,
        timeout_seconds=timeout_seconds,
        allow_empty_checks=allow_empty_checks,
        runner=runner,
        sleep_fn=sleep_fn,
        now_fn=now_fn,
        emit=_emit,
    )
    if wait.exit_code != EXIT_OK:
        return PrLandResult(
            exit_code=wait.exit_code,
            pr=str(pr),
            authorized=True,
            authorization=reason,
            merged=False,
            already_merged=False,
            checks=wait.checks,
            failing=wait.failing,
            pending=wait.pending,
            messages=messages,
            merge_method=merge_method,
        )

    if dry_run:
        _emit("dry_run: checks green — skip merge")
        return PrLandResult(
            exit_code=EXIT_OK,
            pr=str(pr),
            authorized=True,
            authorization=reason,
            merged=False,
            already_merged=False,
            checks=wait.checks,
            messages=messages,
            merge_method=merge_method,
        )

    try:
        merge_pr(pr, method=merge_method, runner=runner)
    except (RuntimeError, ValueError) as exc:
        _emit(f"merge failed: {exc}")
        return PrLandResult(
            exit_code=EXIT_GH_ERROR,
            pr=str(pr),
            authorized=True,
            authorization=reason,
            merged=False,
            already_merged=False,
            checks=wait.checks,
            messages=messages,
            merge_method=merge_method,
        )

    _emit(f"merged PR {pr} via {merge_method}")
    return PrLandResult(
        exit_code=EXIT_OK,
        pr=str(pr),
        authorized=True,
        authorization=reason,
        merged=True,
        already_merged=False,
        checks=wait.checks,
        messages=messages,
        merge_method=merge_method,
    )

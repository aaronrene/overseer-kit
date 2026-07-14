"""Static analysis helpers for desktop-release workflow YAML (§QR.4 / §QR.13)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools.desktop_release.constants import (
    ALL_RELEASE_SECRET_NAMES,
    LINUX_PINNED_RUNNERS,
    MACOS_PINNED_RUNNERS,
)
from tools.desktop_release.refuse import scan_text_for_secret_patterns

FORBIDDEN_PERMISSION_KEYS = frozenset(
    {
        "actions",
        "pull-requests",
        "repository-projects",
        "issues",
        "discussions",
        "packages",
        "pages",
        "security-events",
        "deployments",
        "id-token",  # OIDC write omitted by default (§QR.4.6)
    }
)

ELEVATED_PERMISSION_VALUES = frozenset({"write", "admin"})


def load_workflow(path: Path) -> dict[str, Any]:
    """Parse a GitHub Actions workflow YAML file.

    PyYAML historically maps the unquoted key ``on`` to boolean ``True``;
    normalize that key back to the string ``"on"`` after load.
    """
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"workflow root must be a mapping: {path}")
    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data


def workflow_triggers(data: dict[str, Any]) -> set[str]:
    """Return top-level ``on`` trigger keys."""
    on = data.get("on")
    if on is None and True in data:
        on = data[True]
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return {str(item) for item in on}
    if isinstance(on, dict):
        return {str(key) for key in on.keys()}
    raise ValueError("workflow missing on: triggers")

def matrix_runners(data: dict[str, Any]) -> list[str]:
    """Collect ``runs-on`` values from all jobs (including matrix expansions)."""
    runners: list[str] = []
    jobs = data.get("jobs") or {}
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        runs_on = job.get("runs-on")
        strategy = job.get("strategy") or {}
        matrix = strategy.get("matrix") if isinstance(strategy, dict) else None
        if isinstance(matrix, dict):
            matrix_runners_list = matrix.get("os") or matrix.get("runner") or matrix.get("runs-on")
            if isinstance(matrix_runners_list, list):
                runners.extend(str(item) for item in matrix_runners_list)
                continue
            include = matrix.get("include")
            if isinstance(include, list):
                for row in include:
                    if isinstance(row, dict):
                        for key in ("os", "runner", "runs-on"):
                            if key in row:
                                runners.append(str(row[key]))
                                break
                continue
        if runs_on is not None:
            runners.append(str(runs_on))
    return runners


def assert_release_workflow_contract(data: dict[str, Any]) -> None:
    """Assert frozen release-workflow rules (§QR.4.2–§QR.4.6)."""
    triggers = workflow_triggers(data)
    forbidden = triggers & {"pull_request", "schedule"}
    if forbidden:
        raise AssertionError(f"release workflow forbids triggers: {sorted(forbidden)}")
    if "push" not in triggers and "workflow_dispatch" not in triggers:
        raise AssertionError("release workflow must allow tag push and/or workflow_dispatch")

    perms = data.get("permissions")
    if not isinstance(perms, dict):
        raise AssertionError("release workflow must declare permissions")
    if perms.get("contents") != "write":
        raise AssertionError("permissions.contents must be write")
    for key, value in perms.items():
        if key == "contents":
            continue
        if key in FORBIDDEN_PERMISSION_KEYS and str(value) in ELEVATED_PERMISSION_VALUES:
            raise AssertionError(f"forbidden elevated permission: {key}: {value}")
        if key == "id-token":
            raise AssertionError("id-token must be omitted by default (§QR.4.6)")

    runners = matrix_runners(data)
    has_macos = any(r in MACOS_PINNED_RUNNERS for r in runners)
    has_windows = any("windows" in r for r in runners)
    has_linux = any(r in LINUX_PINNED_RUNNERS or r.startswith("ubuntu-") for r in runners)
    if not (has_macos and has_windows and has_linux):
        raise AssertionError(f"matrix must cover macos/windows/linux; got {runners}")
    for runner in runners:
        if runner == "macos-latest":
            raise AssertionError("macos-latest is forbidden; pin macos-14 or macos-15")
        if runner == "ubuntu-latest":
            raise AssertionError("prefer pinned ubuntu-22.04/24.04 over ubuntu-latest")


def assert_smoke_workflow_contract(data: dict[str, Any]) -> None:
    """Smoke workflow must not publish GitHub Releases."""
    text = yaml.dump(data)
    lowered = text.lower()
    if "softprops/action-gh-release" in lowered:
        raise AssertionError("smoke workflow must not use action-gh-release")
    if "gh release upload" in lowered or "gh release create" in lowered:
        raise AssertionError("smoke workflow must not upload GitHub Releases")
    triggers = workflow_triggers(data)
    if "pull_request" not in triggers and "workflow_dispatch" not in triggers:
        raise AssertionError("smoke workflow should run on pull_request and/or workflow_dispatch")


def workflow_references_secret_names(text: str, names: frozenset[str] | None = None) -> set[str]:
    """Return which §QR.6.2 secret names appear as ``secrets.NAME`` references."""
    wanted = names or ALL_RELEASE_SECRET_NAMES
    found: set[str] = set()
    for name in wanted:
        if f"secrets.{name}" in text:
            found.add(name)
    return found


def assert_workflow_text_clean(path: Path) -> None:
    """Fail if workflow file embeds private-key / password literals."""
    text = path.read_text(encoding="utf-8")
    hits = scan_text_for_secret_patterns(text)
    # Allow secret *references* — scan_text already skips secrets. context for PFX.
    if hits:
        raise AssertionError(f"{path}: secret patterns found: {hits}")

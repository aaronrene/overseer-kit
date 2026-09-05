"""Board filename identity helpers (§MR.6.5)."""

from __future__ import annotations

import re

_NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")


def repo_slug(repo_name: str) -> str:
    """Uppercase ``repo.name`` with non-alnum → ``-`` collapsed (§MR.6.5)."""
    text = (repo_name or "").strip()
    if not text:
        return ""
    collapsed = _NON_ALNUM.sub("-", text).strip("-")
    return collapsed.upper()


def expected_handover_basename(repo_name: str, *, lane: str | None = None) -> str:
    """Default-lane or lane-prefixed handover basename."""
    slug = repo_slug(repo_name)
    if lane and lane.strip() and lane.strip().lower() not in {"product", "default"}:
        return f"{slug}-{lane.strip().upper()}-OVERSEER-HANDOVER.md"
    return f"{slug}-OVERSEER-HANDOVER.md"


def expected_roadmap_basename(repo_name: str, *, lane: str | None = None) -> str:
    """Default-lane or lane-prefixed roadmap basename."""
    slug = repo_slug(repo_name)
    if lane and lane.strip() and lane.strip().lower() not in {"product", "default"}:
        return f"{slug}-{lane.strip().upper()}-ROADMAP.md"
    return f"{slug}-ROADMAP.md"


def expected_handover_title(repo_name: str, *, lane: str | None = None) -> str:
    """Human title including repo (or lane) label."""
    label = (repo_name or "").strip() or "Repo"
    if lane and lane.strip() and lane.strip().lower() not in {"product", "default"}:
        return f"{label} {lane.strip()} Overseer Handover"
    # Title-case-ish: keep slug readable — use repo_name as given.
    pretty = label.replace("-", " ").replace("_", " ")
    if pretty.islower() or pretty.isupper():
        pretty = pretty.title()
    return f"{pretty} Overseer Handover"


def expected_roadmap_title(repo_name: str, *, lane: str | None = None) -> str:
    label = (repo_name or "").strip() or "Repo"
    if lane and lane.strip() and lane.strip().lower() not in {"product", "default"}:
        return f"{label} {lane.strip()} Roadmap"
    pretty = label.replace("-", " ").replace("_", " ")
    if pretty.islower() or pretty.isupper():
        pretty = pretty.title()
    return f"{pretty} Roadmap"


_BARE_HANDOVER = frozenset({"overseer-handover.md"})
_BARE_ROADMAP = frozenset({"roadmap.md"})


def is_bare_legacy_basename(name: str, *, kind: str) -> bool:
    """True when basename is the bare legacy pair (case-insensitive)."""
    base = Path_basename(name).lower()
    if kind == "handover":
        return base in _BARE_HANDOVER
    if kind == "roadmap":
        return base in _BARE_ROADMAP
    return False


def Path_basename(path_or_name: str) -> str:
    """Basename helper without importing pathlib at module top for tests."""
    from pathlib import Path

    return Path(path_or_name).name


def matches_prefixed_pattern(basename: str, repo_name: str, *, kind: str) -> bool:
    """True when basename starts with ``{REPO_SLUG}-`` and matches kind suffix."""
    slug = repo_slug(repo_name)
    if not slug:
        return False
    name = Path_basename(basename)
    if not name.upper().startswith(f"{slug}-"):
        return False
    upper = name.upper()
    if kind == "handover":
        return upper.endswith("-OVERSEER-HANDOVER.MD") or upper.endswith("OVERSEER-HANDOVER.MD")
    if kind == "roadmap":
        return upper.endswith("-ROADMAP.MD") or upper.endswith("ROADMAP.MD")
    return False


def board_name_violation(
    *,
    repo_name: str,
    handover_basename: str | None,
    roadmap_basename: str | None,
    strict: bool,
) -> bool:
    """True when ``strict_board_names`` and board names are bare/unprefixed."""
    if not strict:
        return False
    if handover_basename is None or roadmap_basename is None:
        return True
    if is_bare_legacy_basename(handover_basename, kind="handover"):
        return True
    if is_bare_legacy_basename(roadmap_basename, kind="roadmap"):
        return True
    if not matches_prefixed_pattern(handover_basename, repo_name, kind="handover"):
        return True
    if not matches_prefixed_pattern(roadmap_basename, repo_name, kind="roadmap"):
        return True
    return False


def _first_offending_pair(
    *,
    repo_name: str,
    handover_basename: str,
    roadmap_basename: str,
    lane: str | None = None,
) -> tuple[str, str]:
    """Return ``(offending_basename, compliant_target)`` for the first violation."""
    if is_bare_legacy_basename(handover_basename, kind="handover") or not matches_prefixed_pattern(
        handover_basename, repo_name, kind="handover"
    ):
        return handover_basename, expected_handover_basename(repo_name, lane=lane)
    return roadmap_basename, expected_roadmap_basename(repo_name, lane=lane)


def check_next_unconfigured_advisory(config) -> str:
    """Advisory when ``workspace:`` is absent (§NXP.5). Exit stays 0."""
    repo_name = (config.repo.name or "").strip()
    handover = Path_basename(config.docs.handover)
    roadmap = Path_basename(config.docs.roadmap)
    if board_name_violation(
        repo_name=repo_name,
        handover_basename=handover,
        roadmap_basename=roadmap,
        strict=True,
    ):
        bare, target = _first_offending_pair(
            repo_name=repo_name,
            handover_basename=handover,
            roadmap_basename=roadmap,
        )
        return (
            f"workspace not configured; board name {bare} is bare/legacy — "
            f"prefer {target}"
        )
    return "workspace not configured; board names already compliant"


def status_board_name_advisory(config) -> str | None:
    """Non-blocking bare-board-name advisory for ``ok status`` (§NXP.6).

    Returns ``None`` when ``workspace:`` is configured or boards are compliant.
    Never contributes to ``--exit-code``.
    """
    if config.workspace is not None:
        return None

    repo_name = (config.repo.name or "").strip()

    if config.docs.lanes is None:
        handover = Path_basename(config.docs.handover)
        roadmap = Path_basename(config.docs.roadmap)
        if not board_name_violation(
            repo_name=repo_name,
            handover_basename=handover,
            roadmap_basename=roadmap,
            strict=True,
        ):
            return None
        bare, target = _first_offending_pair(
            repo_name=repo_name,
            handover_basename=handover,
            roadmap_basename=roadmap,
        )
        return f"board naming: {bare} is bare/legacy — prefer {target}"

    offenders: list[tuple[str, str, str]] = []
    for lane_name, lane_docs in config.docs.lanes.items():
        handover = Path_basename(lane_docs.handover)
        roadmap = Path_basename(lane_docs.roadmap)
        if board_name_violation(
            repo_name=repo_name,
            handover_basename=handover,
            roadmap_basename=roadmap,
            strict=True,
        ):
            bare, target = _first_offending_pair(
                repo_name=repo_name,
                handover_basename=handover,
                roadmap_basename=roadmap,
                lane=lane_name,
            )
            offenders.append((lane_name, bare, target))

    if not offenders:
        return None

    _lane, bare, target = offenders[0]
    count = len(offenders)
    return (
        f"board naming: {count} lane{'s' if count != 1 else ''} non-compliant "
        f"(first: {bare} — prefer {target})"
    )
